import os
import sys
import time
import argparse

import requests

OPSLEVEL_API_TOKEN = os.environ.get("OPSLEVEL_API_TOKEN")
OPSLEVEL_ENDPOINT = os.environ.get(
    "OPSLEVEL_ENDPOINT", "https://app.opslevel.com/graphql"
)

MAX_RETRIES = 5
DEFAULT_RETRY_AFTER_SECONDS = 60

EXIT_DELETE_FAILED = 1
EXIT_NOTHING_DELETED = 2

LIST_USERS_QUERY = """
    query users($endCursor: String) {
      account {
        users(first: 500, after: $endCursor) {
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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPSLEVEL_API_TOKEN}",
    }
    data = {"query": query, "variables": variables}
    for attempt in range(MAX_RETRIES + 1):
        response = requests.post(
            OPSLEVEL_ENDPOINT, json=data, headers=headers, timeout=30
        )
        if response.status_code != 429 or attempt == MAX_RETRIES:
            break
        retry_after = response.headers.get("Retry-After", DEFAULT_RETRY_AFTER_SECONDS)
        wait_seconds = max(int(retry_after), 1)
        print(f"Rate limited by OpsLevel, retrying in {wait_seconds}s", file=sys.stderr)
        time.sleep(wait_seconds)

    if response.status_code != 200:
        raise Exception(f"OpsLevel request failed: {response.content.decode()}")
    result = response.json()
    if "errors" in result:
        raise Exception(f"OpsLevel GraphQL errors: {result['errors']}")
    return result


def fetch_users():
    """
    Fetches all users in the account, active and deactivated.
    """
    cursor = None
    has_next_page = True
    users = []
    while has_next_page:
        response = opslevel_graphql_query(
            LIST_USERS_QUERY, variables={"endCursor": cursor}
        )
        nodes = response["data"]["account"]["users"]["nodes"]
        users.extend(nodes)
        page_info = response["data"]["account"]["users"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

    return users


def check_excluded_emails_exist(users, excluded_emails):
    """
    Aborts if an --exclude email matches no user, since a typo would otherwise
    silently let that user be deleted.
    """
    known_emails = {user["email"].lower() for user in users}
    unknown_emails = sorted(excluded_emails - known_emails)
    if unknown_emails:
        fail(
            "These --exclude emails do not match any user in the account: "
            f"{', '.join(unknown_emails)}. Fix them and re-run; nothing was deleted."
        )


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
        response = opslevel_graphql_query(
            DELETE_USER_MUTATION, variables={"id": user["id"]}
        )
    except Exception as e:
        return [str(e)]
    return [error["message"] for error in response["data"]["userDelete"]["errors"]]


def confirm_deletion(count):
    """
    Asks the operator to type 'delete' before anything is removed.
    """
    if not sys.stdin.isatty():
        fail(
            "Refusing to delete without confirmation in a non-interactive session; "
            "pass --yes."
        )
    answer = input(
        f"Permanently delete {count} user(s)? This cannot be undone. "
        "Type 'delete' to confirm: "
    )
    if answer.strip() != "delete":
        fail("Confirmation not given; nothing was deleted.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Permanently delete deactivated OpsLevel users. "
        "Dry run unless --apply is passed."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually delete users (default: dry run)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="skip the confirmation prompt when using --apply",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="EMAIL",
        help="email address to never delete; can be repeated",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    excluded_emails = {email.strip().lower() for email in args.exclude}

    try:
        users = fetch_users()
    except Exception as e:
        fail(f"Could not fetch users: {e}")

    check_excluded_emails_exist(users, excluded_emails)
    deactivated_users = [user for user in users if user["deactivatedAt"]]
    to_delete = select_users_to_delete(deactivated_users, excluded_emails)
    print(
        f"Found {len(deactivated_users)} deactivated user(s), "
        f"{len(to_delete)} eligible for deletion"
    )
    if not to_delete:
        return

    for user in to_delete:
        prefix = "Will delete" if args.apply else "[dry-run] Would delete"
        print(
            f"{prefix}: {user['email']} ({user['name']}), "
            f"deactivated {user['deactivatedAt']}"
        )

    if not args.apply:
        print(
            "Dry run complete; nothing was deleted. "
            "Re-run with --apply to delete the users above."
        )
        return

    if not args.yes:
        confirm_deletion(len(to_delete))

    failed = 0
    for user in to_delete:
        errors = delete_user(user)
        if errors:
            failed += 1
            print(
                f"FAILED to delete {user['email']}: {'; '.join(errors)}",
                file=sys.stderr,
            )
        else:
            print(
                f"Deleted {user['email']} ({user['name']}), "
                f"deactivated {user['deactivatedAt']}"
            )

    print(f"Done: {len(to_delete) - failed} deleted, {failed} failed")
    if failed:
        sys.exit(EXIT_DELETE_FAILED)


if __name__ == "__main__":
    if not OPSLEVEL_API_TOKEN:
        fail("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()
