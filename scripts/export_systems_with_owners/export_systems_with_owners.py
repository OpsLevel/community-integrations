import os
import csv
import requests

OPSLEVEL_API_TOKEN = os.environ.get("OPSLEVEL_API_TOKEN")
OPSLEVEL_ENDPOINT = "https://app.opslevel.com/graphql"

LIST_SYSTEMS_WITH_OWNERS_QUERY = """
    query systemsWithOwners($endCursor: String) {
      account {
        systems(after: $endCursor) {
          nodes {
            name
            owner {
              ... on Team {
                name
              }
            }
          }
          pageInfo {
            endCursor
            hasNextPage
          }
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
    response = requests.post(OPSLEVEL_ENDPOINT, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"OpsLevel request failed: {response.content.decode()}")
    result = response.json()
    if "errors" in result:
        raise Exception(f"OpsLevel GraphQL errors: {result['errors']}")
    return result


def fetch_systems():
    """
    Fetches all systems and their owning team from OpsLevel.
    Owner will be empty for systems with no Team owner set.
    """
    cursor = None
    has_next_page = True
    systems = []  # Store fetched systems
    while has_next_page:
        response = opslevel_graphql_query(
            LIST_SYSTEMS_WITH_OWNERS_QUERY, variables={"endCursor": cursor}
        )
        nodes = response["data"]["account"]["systems"]["nodes"]
        systems.extend(nodes)
        page_info = response["data"]["account"]["systems"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

    return systems


def export_to_csv(systems, filename="systems_with_owners.csv"):
    """
    Writes the collected systems list to a CSV file, one row per system.
    """
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "owner"])
        for system in systems:
            owner_name = system["owner"]["name"] if system["owner"] else ""
            writer.writerow([system["name"], owner_name])
    print(f"CSV file has been created at {filename}")


def main():
    systems = fetch_systems()
    export_to_csv(systems)


if __name__ == "__main__":
    if not OPSLEVEL_API_TOKEN:
        raise ValueError("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()
