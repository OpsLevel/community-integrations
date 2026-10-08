import os
import sys
import argparse

import requests

OPSLEVEL_API_TOKEN = os.environ.get("OPSLEVEL_API_TOKEN")
OPSLEVEL_ENDPOINT = os.environ.get("OPSLEVEL_ENDPOINT", "https://app.opslevel.com/graphql")

LIST_DEACTIVATED_USERS_QUERY = """
    query deactivatedUsers($endCursor: String) {
      account {
        users(after: $endCursor, filter: [{ key: deactivated_at, type: does_not_equal }]) {
          nodes {
            id
            name
            email
            deactivatedAt
          }
          pageInfo {
            endCursor
            hasNextPage
          }
        }
      }
    }
"""

DELETE_USER_MUTATION = """
    mutation deleteUser($id: ID!) {
      userDelete(user: { id: $id }) {
        errors {
          message
        }
      }
    }
"""


def opslevel_graphql_query(query, variables=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPSLEVEL_API_TOKEN}",
    }
    data = {"query": query, "variables": variables}
    response = requests.post(OPSLEVEL_ENDPOINT, json=data, headers=headers, timeout=30)
    if response.status_code != 200:
        raise Exception(f"OpsLevel request failed: {response.content.decode()}")
    result = response.json()
    if "errors" in result:
        raise Exception(f"OpsLevel GraphQL errors: {result['errors']}")
    return result


def fetch_deactivated_users():
    """
    Fetches all deactivated users from OpsLevel.
    """
    cursor = None
    has_next_page = True
    users = []
    while has_next_page:
        response = opslevel_graphql_query(
            LIST_DEACTIVATED_USERS_QUERY, variables={"endCursor": cursor}
        )
        nodes = response["data"]["account"]["users"]["nodes"]
        users.extend(nodes)
        page_info = response["data"]["account"]["users"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

    return users


def select_users_to_delete(users, excluded_emails):
    """
    Keeps only deactivated users who are not in the exclude list.
    """
    to_delete = []
    for user in users:
        if not user["deactivatedAt"]:
            continue
        if user["email"].lower() in excluded_emails:
            print(f"Skipping {user['email']}: excluded")
        else:
            to_delete.append(user)

    return to_delete


def delete_user(user):
    """
    Deletes a single user. Returns a list of error messages, empty on success.
    """
    try:
        response = opslevel_graphql_query(DELETE_USER_MUTATION, variables={"id": user["id"]})
    except Exception as e:
        return [str(e)]
    return [error["message"] for error in response["data"]["userDelete"]["errors"]]


def confirm_deletion(count):
    """
    Asks the operator to type 'delete' before anything is removed.
    """
    if not sys.stdin.isatty():
        raise SystemExit("Refusing to delete without confirmation in a non-interactive session; pass --yes.")
    answer = input(f"Permanently delete {count} user(s)? This cannot be undone. Type 'delete' to confirm: ")
    if answer.strip() != "delete":
        raise SystemExit("Confirmation not given; nothing was deleted.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Permanently delete deactivated OpsLevel users. Dry run unless --apply is passed."
    )
    parser.add_argument("--apply", action="store_true", help="actually delete users (default: dry run)")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt when using --apply")
    parser.add_argument("--exclude", action="append", default=[], metavar="EMAIL",
                        help="email address to never delete; can be repeated")
    return parser.parse_args()


def main():
    args = parse_args()
    excluded_emails = {email.strip().lower() for email in args.exclude}

    users = fetch_deactivated_users()
    to_delete = select_users_to_delete(users, excluded_emails)
    print(f"Found {len(users)} deactivated user(s), {len(to_delete)} eligible for deletion")
    if not to_delete:
        return

    for user in to_delete:
        prefix = "Will delete" if args.apply else "[dry-run] Would delete"
        print(f"{prefix}: {user['email']} ({user['name']}), deactivated {user['deactivatedAt']}")

    if not args.apply:
        print("Dry run complete; nothing was deleted. Re-run with --apply to delete the users above.")
        return

    if not args.yes:
        confirm_deletion(len(to_delete))

    failed = 0
    for user in to_delete:
        errors = delete_user(user)
        if errors:
            failed += 1
            print(f"FAILED to delete {user['email']}: {'; '.join(errors)}", file=sys.stderr)
        else:
            print(f"Deleted {user['email']} ({user['name']}), deactivated {user['deactivatedAt']}")

    print(f"Done: {len(to_delete) - failed} deleted, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    if not OPSLEVEL_API_TOKEN:
        raise ValueError("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()
