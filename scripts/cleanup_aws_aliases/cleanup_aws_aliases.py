import os
import sys
import time
import argparse

import requests

OPSLEVEL_API_TOKEN = os.environ.get("OPSLEVEL_API_TOKEN")
OPSLEVEL_ENDPOINT = os.environ.get("OPSLEVEL_ENDPOINT", "https://app.opslevel.com/graphql")

MAX_RETRIES = 5
DEFAULT_RETRY_AFTER_SECONDS = 60
MAX_RETRY_AFTER_SECONDS = 300

EXIT_DELETE_FAILED = 1
EXIT_NOTHING_DELETED = 2

LIST_COMPONENTS_QUERY = """
    query components($endCursor: String) {
      account {
        services(first: 100, after: $endCursor) {
          nodes { name slug aliases }
          pageInfo { endCursor hasNextPage }
        }
      }
    }
"""

DELETE_ALIAS_MUTATION = """
    mutation deleteAlias($alias: String!) {
      aliasDelete(input: { alias: $alias, ownerType: service }) {
        errors { message }
      }
    }
"""


def fail(message):
    """
    Exits without deleting anything, using an exit code distinct from failed deletions.
    """
    print(message, file=sys.stderr)
    sys.exit(EXIT_NOTHING_DELETED)


def opslevel_graphql_query(query, variables=None):
    """
    Sends a GraphQL request, waiting and retrying when OpsLevel rate limits the token.
    """
    headers = {"Authorization": f"Bearer {OPSLEVEL_API_TOKEN}"}
    for attempt in range(MAX_RETRIES + 1):
        response = requests.post(
            OPSLEVEL_ENDPOINT, json={"query": query, "variables": variables}, headers=headers, timeout=30
        )
        if response.status_code != 429 or attempt == MAX_RETRIES:
            break
        try:
            wait_seconds = int(response.headers["Retry-After"])
        except (KeyError, ValueError):
            wait_seconds = DEFAULT_RETRY_AFTER_SECONDS
        wait_seconds = min(max(wait_seconds, 1), MAX_RETRY_AFTER_SECONDS)
        print(f"Rate limited by OpsLevel, retrying in {wait_seconds}s", file=sys.stderr)
        time.sleep(wait_seconds)

    if response.status_code != 200:
        raise Exception(f"OpsLevel request failed: {response.content.decode()}")
    result = response.json()
    if "errors" in result:
        raise Exception(f"OpsLevel GraphQL errors: {result['errors']}")
    return result["data"]


def find_stale_aliases(prefix):
    """
    Returns (component name, alias) for each alias "X" on a component that also has
    "<prefix>X". Never returns the component's slug (its locked primary alias) or an ARN.
    """
    cursor = None
    stale = []
    while True:
        services = opslevel_graphql_query(LIST_COMPONENTS_QUERY, {"endCursor": cursor})["account"]["services"]
        for component in services["nodes"]:
            aliases = set(component["aliases"])
            for alias in sorted(aliases):
                old_alias = alias[len(prefix):]
                if (
                    alias.startswith(prefix)
                    and old_alias in aliases
                    and old_alias != component["slug"]
                    and not old_alias.startswith("arn:")
                ):
                    stale.append((component["name"], old_alias))
        if not services["pageInfo"]["hasNextPage"]:
            return stale
        cursor = services["pageInfo"]["endCursor"]


def delete_alias(alias):
    """
    Deletes a single alias. Returns a list of error messages, empty on success.
    """
    try:
        response = opslevel_graphql_query(DELETE_ALIAS_MUTATION, {"alias": alias})
    except Exception as e:
        return [str(e)]
    return [error["message"] for error in response["aliasDelete"]["errors"]]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Delete aliases left behind after prefixing component names. "
        "Dry run unless --apply is passed."
    )
    parser.add_argument("--apply", action="store_true", help="actually delete aliases (default: dry run)")
    parser.add_argument("--prefix", default="aws-", help="prefix added to component names (default: aws-)")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        stale = find_stale_aliases(args.prefix)
    except Exception as e:
        fail(f"Could not fetch components: {e}")

    print(f"Found {len(stale)} alias(es) eligible for deletion")
    if not stale:
        return

    for name, alias in stale:
        label = "Will delete" if args.apply else "[dry-run] Would delete"
        print(f"{label}: {alias} (component: {name})")

    if not args.apply:
        print("Dry run complete; nothing was deleted. Re-run with --apply to delete the aliases above.")
        return

    failed = 0
    for name, alias in stale:
        errors = delete_alias(alias)
        if errors:
            failed += 1
            print(f"FAILED to delete {alias} (component: {name}): {'; '.join(errors)}", file=sys.stderr)
        else:
            print(f"Deleted {alias} (component: {name})")

    print(f"Done: {len(stale) - failed} deleted, {failed} failed")
    if failed:
        sys.exit(EXIT_DELETE_FAILED)


if __name__ == "__main__":
    if not OPSLEVEL_API_TOKEN:
        fail("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()
