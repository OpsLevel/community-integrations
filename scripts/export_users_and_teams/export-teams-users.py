import requests
import json
import csv
import os

def get_all_teams_and_users(api_token):
    """
    Retrieves all teams and their users from OpsLevel using the GraphQL API.

    Args:
        api_token (str): The OpsLevel API token.

    Returns:
        list: A list of team data dictionaries.
    """

    url = "https://api.opslevel.com/graphql"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    query = """
    query get_all_teams($endCursor: String) {
      account {
        teams(after: $endCursor) {
          nodes {
            id
            alias
            aliases
            contacts {
              type
              displayName
              address
            }
            memberships {
              nodes {
                user {
                  id
                  name
                  email
                }
                role
              }
            }
            responsibilities
          }
          pageInfo{
            endCursor
            hasNextPage
          }
        }
      }
    }
    """

    end_cursor = None
    all_teams_data = []
    has_next_page = True

    while has_next_page:
        variables = {"endCursor": end_cursor}
        payload = {"query": query, "variables": variables}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if data and data.get("data") and data["data"].get("account") and data["data"]["account"].get("teams"):
                teams = data["data"]["account"]["teams"]["nodes"]
                all_teams_data.extend(teams)

                page_info = data["data"]["account"]["teams"]["pageInfo"]
                end_cursor = page_info["endCursor"]
                has_next_page = page_info["hasNextPage"]
            else:
                print("Error: Invalid response from OpsLevel API.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from OpsLevel API: {e}")
            return None

    return all_teams_data

def export_teams_and_users_to_csv(teams_data, output_csv_path):
    """
    Exports team and user data to a CSV file.

    Args:
        teams_data (list): A list of team data dictionaries.
        output_csv_path (str, optional): The path to the CSV file to create. Defaults to "teams_and_users.csv".
    """

    try:
        with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow([
                "Team ID", "Team Alias", "Team Aliases", "Contact Type", "Contact Display Name",
                "Contact Address", "User ID", "User Name", "User Email", "Membership Role", "Responsibilities"
            ])

            for team in teams_data:
                team_name = team.get("name", "")
                team_alias = team.get("alias", "")
                #team_aliases = ", ".join(team.get("aliases", []))

                contacts = team.get("contacts", [])
                memberships = team.get("memberships", {}).get("nodes", [])

                if contacts:
                    for contact in contacts:
                        contact_type = contact.get("type", "")
                        display_name = contact.get("displayName", "")
                        address = contact.get("address", "")

                        if memberships:
                            for membership in memberships:
                                user = membership.get("user", {})
                                user_id = user.get("id", "")
                                user_name = user.get("name", "")
                                user_email = user.get("email", "")
                                role = membership.get("role", "")
                                writer.writerow([
                                    team_name, team_alias, contact_type, display_name,
                                    address, user_id, user_name, user_email, role
                                ])
                        else:
                            writer.writerow([
                                team_name, team_alias, contact_type, display_name,
                                address, "", "", "", ""
                            ])

                elif memberships:
                    for membership in memberships:
                        user = membership.get("user", {})
                        user_id = user.get("id", "")
                        user_name = user.get("name", "")
                        user_email = user.get("email", "")
                        role = membership.get("role", "")
                        writer.writerow([
                            team_name, team_alias, "", "", "", user_id, user_name, user_email, role
                        ])
                else:
                    writer.writerow([team_name, team_alias, "", "", "", "", "", "", ""])

        print(f"Data exported to {output_csv_path}")

    except IOError as e:
        print(f"Error writing to CSV file: {e}")

if __name__ == "__main__":
    api_token = os.environ.get("OPSLEVEL_API_TOKEN")
    output_csv_path = os.environ.get("OUTPUT_CSV_PATH")

    if not api_token or not output_csv_path:
        print("Error: OPSLEVEL_API_TOKEN and OUTPUT_CSV_PATH environment variables must be set.")
        exit(1)

    teams_data = get_all_teams_and_users(api_token)
    if teams_data:
        export_teams_and_users_to_csv(teams_data, output_csv_path)

