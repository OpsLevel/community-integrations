#!/usr/bin/env python3
"""Attach Datadog monitors to OpsLevel components only when they are tagged env:prd.

Links monitors tagged `service:<alias>` + `env:prd` to the component with that alias,
and removes links from monitors tagged with any other env.

Usage:
  OPSLEVEL_API_TOKEN=... python sync_datadog_prd_monitors.py                  # dry run
  OPSLEVEL_API_TOKEN=... python sync_datadog_prd_monitors.py --apply          # make changes
  OPSLEVEL_API_TOKEN=... python sync_datadog_prd_monitors.py --reset          # dry run of the one-time cleanup
  OPSLEVEL_API_TOKEN=... python sync_datadog_prd_monitors.py --reset --apply  # remove every link except
                                                                               # env:prd monitors' own components

Options:
  --env production         keep a different env linked (default: prd)
  --service-key app        read the component from a different tag key (default: service)
  OPSLEVEL_ENDPOINT=...    use a different OpsLevel API URL (default: https://app.opslevel.com/graphql)
"""
import os
import re
import sys
import argparse

import requests

OPSLEVEL_API_TOKEN = os.environ.get("OPSLEVEL_API_TOKEN")
OPSLEVEL_ENDPOINT = os.environ.get("OPSLEVEL_ENDPOINT", "https://app.opslevel.com/graphql")

LIST_ALERT_SOURCES_QUERY = """
    query alertSources($endCursor: String) {
      account {
        alertSources(first: 100, after: $endCursor) {
          nodes {
            id name type metadata
            alertSourceServices { nodes { id service { id aliases } } }
          }
          pageInfo { endCursor hasNextPage }
        }
      }
    }
"""

LINK_MUTATION = """
    mutation link($alertSourceId: ID!, $alias: String!) {
      alertSourceServiceCreate(input: { alertSourceId: $alertSourceId, service: { alias: $alias } }) {
        errors { message }
      }
    }
"""

UNLINK_MUTATION = """
    mutation unlink($id: ID!) {
      alertSourceServiceDelete(input: { id: $id }) {
        errors { message }
      }
    }
"""


def fail(message):
    """
    Prints the message and exits without changing anything.
    """
    print(message, file=sys.stderr)
    sys.exit(1)


def opslevel_graphql_query(query, variables=None):
    """
    Sends a GraphQL request and returns its data, raising on HTTP or GraphQL errors.
    """
    headers = {"Authorization": f"Bearer {OPSLEVEL_API_TOKEN}"}
    response = requests.post(
        OPSLEVEL_ENDPOINT, json={"query": query, "variables": variables}, headers=headers, timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"OpsLevel request failed: {response.content.decode()}")
    result = response.json()
    if "errors" in result:
        raise Exception(f"OpsLevel GraphQL errors: {result['errors']}")
    return result["data"]


def list_datadog_alert_sources():
    """
    Returns every Datadog alert source (monitor) with its current component links.
    Fetches all pages before anything changes, so unlinking can't shift the pagination.
    """
    cursor = None
    sources = []
    while True:
        page = opslevel_graphql_query(LIST_ALERT_SOURCES_QUERY, {"endCursor": cursor})["account"]["alertSources"]
        sources += [source for source in page["nodes"] if source["type"] == "datadog"]
        if not page["pageInfo"]["hasNextPage"]:
            return sources
        cursor = page["pageInfo"]["endCursor"]


def monitor_tags(source, service_key):
    """
    Returns (envs, service aliases) read from the monitor's `env:` and `<service_key>:` tags.
    """
    # The API returns metadata as a string whose format isn't guaranteed to be JSON, so this
    # picks out quoted "env:..." and "<service_key>:..." strings rather than parsing it. Any other
    # quoted metadata value starting with one of those prefixes would also match.
    pattern = re.compile(r'"((?:%s|env):[^"]+)"' % re.escape(service_key))
    tags = pattern.findall(source["metadata"] or "")
    envs = {tag.split(":", 1)[1] for tag in tags if tag.startswith("env:")}
    aliases = {tag.split(":", 1)[1].strip() for tag in tags if tag.startswith(f"{service_key}:")}
    return envs, aliases


def component_label(link):
    aliases = link["service"]["aliases"]
    return aliases[0] if aliases else link["service"]["id"]


def plan_changes(sources, env, service_key, reset):
    """
    Returns the links to remove and the links to add, as lists of dicts.
    - Monitors tagged `env:<env>` are linked to the component in each `<service_key>:` tag.
    - Monitors tagged with any other env are unlinked.
    - Monitors with no env tag are left alone, unless `reset` is set.
    - With `reset`, every link is removed except an `env:<env>` monitor's link to a component
      named in its own tags, so correct links are never removed and added back.
    """
    unlinks = []
    links = []
    for source in sources:
        envs, aliases = monitor_tags(source, service_key)
        wanted_aliases = aliases if env in envs else set()
        current_links = source["alertSourceServices"]["nodes"]

        if reset:
            reason = "reset"
        elif envs and env not in envs:
            reason = f"env {', '.join(sorted(envs))}"
        else:
            reason = None

        if reason:
            kept_links = []
            for link in current_links:
                if wanted_aliases & set(link["service"]["aliases"]):
                    kept_links.append(link)
                else:
                    unlinks.append(
                        {"id": link["id"], "monitor": source["name"], "component": component_label(link), "reason": reason}
                    )
            current_links = kept_links

        linked_aliases = {alias for link in current_links for alias in link["service"]["aliases"]}
        for alias in sorted(wanted_aliases - linked_aliases):
            links.append({"alertSourceId": source["id"], "monitor": source["name"], "component": alias})
    return unlinks, links


def run_mutation(mutation, variables, payload_key):
    """
    Runs a single link/unlink mutation. Returns a list of error messages, empty on success.
    """
    try:
        response = opslevel_graphql_query(mutation, variables)
    except Exception as e:
        return [str(e)]
    return [error["message"] for error in response[payload_key]["errors"]]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Link Datadog monitors to OpsLevel components only when they are tagged with the "
        "chosen env, and unlink monitors tagged with any other env. Dry run unless --apply is passed."
    )
    parser.add_argument("--apply", action="store_true", help="actually change links (default: dry run)")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="also remove links from monitors with no env tag and links to components not in a monitor's "
        "own tags (one-time cleanup)",
    )
    parser.add_argument("--env", default="prd", help="env tag value to keep linked (default: prd)")
    parser.add_argument(
        "--service-key", default="service", help="tag key naming the component alias (default: service)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        sources = list_datadog_alert_sources()
    except Exception as e:
        fail(f"Could not fetch alert sources: {e}")

    unlinks, links = plan_changes(sources, args.env, args.service_key, args.reset)

    print(f"Found {len(sources)} Datadog monitor(s): {len(unlinks)} link(s) to remove, {len(links)} link(s) to add")
    if not unlinks and not links:
        return

    for change in unlinks:
        label = "Will unlink" if args.apply else "[dry-run] Would unlink"
        print(f"{label}: {change['monitor']} from {change['component']} ({change['reason']})")
    for change in links:
        label = "Will link" if args.apply else "[dry-run] Would link"
        print(f"{label}: {change['monitor']} to {change['component']}")

    if not args.apply:
        print("Dry run complete; nothing was changed. Re-run with --apply to make the changes above.")
        return

    failed = 0
    for change in unlinks:
        errors = run_mutation(UNLINK_MUTATION, {"id": change["id"]}, "alertSourceServiceDelete")
        if errors:
            failed += 1
            print(
                f"FAILED to unlink {change['monitor']} from {change['component']}: {'; '.join(errors)}",
                file=sys.stderr,
            )
        else:
            print(f"Unlinked {change['monitor']} from {change['component']}")

    for change in links:
        variables = {"alertSourceId": change["alertSourceId"], "alias": change["component"]}
        errors = run_mutation(LINK_MUTATION, variables, "alertSourceServiceCreate")
        if errors:
            failed += 1
            print(
                f"FAILED to link {change['monitor']} to {change['component']}: {'; '.join(errors)}",
                file=sys.stderr,
            )
        else:
            print(f"Linked {change['monitor']} to {change['component']}")

    total = len(unlinks) + len(links)
    print(f"Done: {total - failed} changed, {failed} failed")
    if failed:
        print("Re-run the same command to retry the failed changes.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if not OPSLEVEL_API_TOKEN:
        fail("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()
