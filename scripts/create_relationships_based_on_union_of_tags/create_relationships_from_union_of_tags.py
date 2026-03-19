#!/usr/bin/env python3
"""
Create OpsLevel relationships between default (service) components and infrastructure
components based on tag matching. Reads relationship definitions whose description
contains service_tag_key, parses tag rules, and creates relationships when
infrastructure tags match (environment_tag_key:environment_tag_value and
service_tag_key:<default_component_alias>).
"""

import argparse
import os
import sys
import time
from typing import Any, Optional

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

OPSLEVEL_ENDPOINT = "https://app.opslevel.com/graphql"

# ---------------------------------------------------------------------------
# GraphQL documents
# ---------------------------------------------------------------------------

QUERY_RELATIONSHIP_DEFINITIONS = gql(
"""
    query relationshipDefinitions($endCursor: String) {
      account {
        relationshipDefinitions(after: $endCursor, componentType: { alias: "service" }) {
          nodes {
            id
            name
            description
            componentType {
              name
              alias
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
"""
)

QUERY_GET_COMPONENTS = gql(
    """
    query get_components($endCursor: String, $componentCategory: String!) {
      account {
        services(after: $endCursor, componentCategory: $componentCategory) {
          pageInfo {
            endCursor
            hasNextPage
          }
          nodes {
            id
            name
            aliases
            tags {
              nodes {
                key
                value
                id
              }
            }
          }
        }
      }
    }
    """
)

MUTATION_RELATIONSHIP_CREATE = gql(
"""
    mutation relationshipCreate(
      $source: IdentifierInput!,
      $target: IdentifierInput!,
      $type: RelationshipTypeEnum!,
      $relationshipDefinition: IdentifierInput
    ) {
      relationshipCreate(
        relationshipDefinition: {
          source: $source,
          target: $target,
          type: $type,
          relationshipDefinition: $relationshipDefinition
        }
      ) {
        relationship {
          id
          type
          source { __typename }
          target { __typename }
        }
        errors {
          message
          path
        }
      }
    }
"""
)


# ---------------------------------------------------------------------------
# Parsing rules from relationship definition description
# ---------------------------------------------------------------------------

def parse_description_key_value(description: Optional[str]) -> dict[str, str]:
    """Parse comma-separated key:value pairs from description. Trim spaces."""
    result: dict[str, str] = {}
    if not description or not description.strip():
        return result
    # Split on comma, then each part on first colon
    for part in description.split(","):
        part = part.strip()
        if ":" not in part:
            continue
        key, _, value = part.partition(":")
        key = key.strip()
        value = value.strip()
        if key and value:
            result[key] = value
    return result


def extract_rules_from_definition(node: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    If definition has 'service_tag_key' in description, parse and return a rule dict.
    Returns None if skipped. Logs a warning when description has service_tag_key
    but is missing environment_tag_key or environment_tag_value.
    """
    description = (node.get("description") or "")
    if "service_tag_key" not in description:
        return None
    parsed = parse_description_key_value(description)
    service_tag_key = parsed.get("service_tag_key")
    environment_tag_key = parsed.get("environment_tag_key")
    environment_tag_value = parsed.get("environment_tag_value")
    if not service_tag_key or not environment_tag_key or not environment_tag_value:
        name = node.get("name") or node.get("id") or "unknown"
        print(
            f"  Warning: Skipping relationship definition '{name}': description contains "
            "service_tag_key but is missing environment_tag_key or environment_tag_value. "
            "Expected comma-separated key:value pairs, e.g. "
            "service_tag_key:service,environment_tag_key:environment,environment_tag_value:staging",
            file=sys.stderr,
        )
        return None
    return {
        "relationship_definition_id": node["id"],
        "relationship_definition_name": node.get("name") or "unknown",
        "service_tag_key": service_tag_key,
        "environment_tag_key": environment_tag_key,
        "environment_tag_value": environment_tag_value,
    }


# ---------------------------------------------------------------------------
# Tag matching (case-sensitive)
# ---------------------------------------------------------------------------

def get_tag_map(tags_nodes: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Build key -> list of values from tags.nodes (one key can have multiple values)."""
    out: dict[str, list[str]] = {}
    for t in tags_nodes or []:
        k = (t.get("key") or "").strip()
        v = (t.get("value") or "").strip()
        if not k:
            continue
        if k not in out:
            out[k] = []
        out[k].append(v)
    return out


def infrastructure_matches_rule(
    infra: dict[str, Any],
    rule: dict[str, Any],
    default_aliases: list[str],
) -> bool:
    """
    Infra must have (environment_tag_key, environment_tag_value) and
    (service_tag_key, v) where v is in default_aliases (case-sensitive).
    """
    tags = get_tag_map((infra.get("tags") or {}).get("nodes") or [])
    env_key = rule["environment_tag_key"]
    env_val = rule["environment_tag_value"]
    svc_key = rule["service_tag_key"]
    if env_key not in tags or env_val not in tags[env_key]:
        return False
    if svc_key not in tags:
        return False
    for v in tags[svc_key]:
        if v in default_aliases:
            return True
    return False


# ---------------------------------------------------------------------------
# GraphQL client and pagination
# ---------------------------------------------------------------------------

def make_client(token: str) -> Client:
    transport = RequestsHTTPTransport(
        url=OPSLEVEL_ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        verify=True,
    )
    return Client(transport=transport, fetch_schema_from_transport=False)


def execute(client: Client, document: Any, variables: Optional[dict] = None) -> dict:
    """Execute a query or mutation and return the raw result (data payload)."""
    return client.execute(document, variable_values=variables or {})


def paginate(
    client: Client,
    document: Any,
    path: list[str],
    variables_extra: Optional[dict] = None,
    verbose: bool = False,
) -> list[dict]:
    """Follow pageInfo.hasNextPage / endCursor and collect all nodes."""
    all_nodes: list[dict] = []
    cursor: Optional[str] = None
    page = 0
    while True:
        variables = dict(variables_extra or {})
        if cursor is not None:
            variables["endCursor"] = cursor
        data = execute(client, document, variables)
        current = data
        for key in path[:-1]:
            current = (current or {}).get(key, {})
        conn = (current or {}).get(path[-1])
        if not conn:
            break
        nodes = conn.get("nodes") or []
        all_nodes.extend(nodes)
        page_info = conn.get("pageInfo") or {}
        has_next = page_info.get("hasNextPage")
        if verbose:
            print(f"  Page index {page}: got {len(nodes)} nodes (total {len(all_nodes)})")
        if not has_next:
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break
        page += 1
    return all_nodes


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create OpsLevel relationships from union of tags (default <-> infrastructure)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print what would be created; do not call relationshipCreate.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log pagination and progress.",
    )
    args = parser.parse_args()

    token = os.environ.get("OPSLEVEL_API_TOKEN")
    if not token or not token.strip():
        print("Error: OPSLEVEL_API_TOKEN environment variable is required.", file=sys.stderr)
        return 1

    client = make_client(token.strip())

    # 1) Fetch relationship definitions and build rules
    if args.verbose:
        print("Fetching relationship definitions...")
    def_nodes = paginate(
        client,
        QUERY_RELATIONSHIP_DEFINITIONS,
        ["account", "relationshipDefinitions"],
        verbose=args.verbose,
    )
    rules: list[dict[str, Any]] = []
    for node in def_nodes:
        rule = extract_rules_from_definition(node)
        if rule:
            rules.append(rule)
    if args.verbose:
        print(f"Found {len(rules)} rules with service_tag_key in description.")

    if not rules:
        print("No relationship definitions with service_tag_key in description. Nothing to do.")
        return 0

    # 2) Fetch default and infrastructure components
    if args.verbose:
        print("Fetching default components...")
    default_components = paginate(
        client,
        QUERY_GET_COMPONENTS,
        ["account", "services"],
        variables_extra={"componentCategory": "default"},
        verbose=args.verbose,
    )
    if args.verbose:
        print("Fetching infrastructure components...")
    infra_components = paginate(
        client,
        QUERY_GET_COMPONENTS,
        ["account", "services"],
        variables_extra={"componentCategory": "infrastructure"},
        verbose=args.verbose,
    )
    if args.verbose:
        print(f"Default components: {len(default_components)}, Infrastructure: {len(infra_components)}.")

    # 3) Match: for each rule and each default component, find infra with both tags
    to_create: list[tuple[dict, dict, dict]] = []  # (default_component, infra_component, rule)
    for rule in rules:
        for default_comp in default_components:
            aliases = list(default_comp.get("aliases") or [])
            for infra in infra_components:
                if infrastructure_matches_rule(infra, rule, aliases):
                    to_create.append((default_comp, infra, rule))

    print(f"Relationships to create: {len(to_create)}")
    if not to_create:
        return 0

    if args.dry_run:
        for default_comp, infra, rule in to_create:
            print(
                f"  [dry-run] {default_comp.get('name')} ({default_comp['id']}) --[{rule['relationship_definition_name']}]--> "
                f"{infra.get('name')} ({infra['id']})"
            )
        return 0

    # 4) Call relationshipCreate for each
    created = 0
    failed = 0
    for default_comp, infra, rule in to_create:
        variables = {
            "source": {"id": default_comp["id"]},
            "target": {"id": infra["id"]},
            "type": "related_to",
            "relationshipDefinition": {"id": rule["relationship_definition_id"]},
        }
        try:
            data = execute(client, MUTATION_RELATIONSHIP_CREATE, variables)
            create_result = (data or {}).get("relationshipCreate")
            errors = (create_result or {}).get("errors") or []
            if errors:
                for err in errors:
                    print(
                        f"  Error creating {default_comp.get('name')} -> {infra.get('name')} "
                        f"[{rule['relationship_definition_name']}]: {err.get('message', err)}",
                        file=sys.stderr,
                    )
                failed += 1
            else:
                created += 1
                print(f"  Created: {default_comp.get('name')} -> {infra.get('name')} [{rule['relationship_definition_name']}]")
        except Exception as e:
            print(
                f"  Exception for {default_comp.get('name')} -> {infra.get('name')}: {e}",
                file=sys.stderr,
            )
            failed += 1
        time.sleep(0.1)

    print(f"Created: {created}, Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
