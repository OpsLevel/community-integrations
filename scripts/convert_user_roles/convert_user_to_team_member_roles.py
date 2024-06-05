import os
import requests

OPSLEVEL_API_TOKEN = os.environ["OPSLEVEL_API_TOKEN"]
OPSLEVEL_ENDPOINT = "https://app.opslevel.com/graphql"

LIST_USERS_QUERY = """
    query roles($endCursor: String) {
      account {
        users(filter: {key: role, arg: "user", type: equals}, after: $endCursor) {
          nodes {
            id
            email
            name
            role
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """

UPDATE_USER_ROLE_MUTATION = """
    mutation update_user_role($email: String, $role: UserRole) {
      userUpdate(user: {email: $email}, input: {role: $role}) {
        user {
          id
          email
          name
          role
        }
        errors {
          message
          path
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
    return response.json()

def fetch_users():
    """Fetch list of users from OpsLevel."""
    cursor = None
    has_next_page = True
    users = []  # Store fetched users
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

# define main function for a graphql query of a list of users, prompting the user to select a role from a static list of options, then running a graphql mutation to change all users to that role
def main():
    # get list of users
    users = fetch_users()
    # print list of users
    print("List of users:")
    for user in users:
        print(f"Role: {user['role']}, Email: {user['email']}, Name: {user['name']}, ")

    # prompt user to confirm they want to change all users to the "team_member" role
    confirm = input("Are you sure you want to change all users to the 'team_member' role? (y/n) ")
    # if n, exit
    if confirm.lower() == "n":
        print("Exiting...")
        return
    elif confirm.lower() == "y":
        # loop through each user and run graphql mutation to change all users to the selected role
        for user in users:
            response = opslevel_graphql_query(
                UPDATE_USER_ROLE_MUTATION,
                variables={"email": user["email"], "role": "team_member"},
            )
            print("Mutation executed.")
            print(response)
    else:
        print("Invalid input. Exiting...")
        return

if __name__ == "__main__":
    if OPSLEVEL_API_TOKEN is None:
        raise ValueError("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()