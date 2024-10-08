import requests
import json

# Replace with your GraphQL endpoint and set up the API token as an env variable
OPSLEVEL_API_TOKEN = os.environ["OPSLEVEL_API_TOKEN"]
GRAPHQL_ENDPOINT = 'https://api.opslevel.com/graphql'

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    'Content-Type': 'application/json'
}

def run_query(query, variables=None):
    """Function to send queries to the OpsLevel GraphQL API"""
    #print(query)
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    response = requests.post(
        GRAPHQL_ENDPOINT, 
        headers=HEADERS, 
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}. Response: {response.text}")
    
def get_all_teams():
    """Fetch the teams"""
    query = """
    query get_all_teams {
    account {
        teams {
            edges {
                node {
                id
                name
                aliases
                responsibilities
                    }
                }
            }
        }
    }
    """
    
    result = run_query(query)
    #print(result)
    return result['data']['account']['teams']['edges']


# Function to create a system for each team
def create_system_for_team(name, description, aliases):
    """Create a system in OpsLevel using the team details"""
    mutation = """
    mutation system_create($name: String, $description: String, $ownerId: ID, $parent: IdentifierInput, $note: String) {
    systemCreate(
        input: {name: $name, description: $description, ownerId: $ownerId, parent: $parent, note: $note}
    ) {
        system {
            id
            name
            description
            note
        }
        errors {
            message
            path
            __typename
            }
        }
    }
    """
    
    variables = {
        "name": name,
        "note": description,
        "description": name
    }
    
    result = run_query(mutation, variables)
    return result

def main():
    
    # Step 1: Call the API to get all teams
    teams = get_all_teams()
    print(teams)
    
    if len(teams) > 0:
            # Step 2: Loop through teams and create systems
        for team in teams:
            create_system_for_team(team['node']['name'], team['node']['responsibilities'],team['node']['aliases'] )
    else:
        print("No teams found.")

if __name__ == "__main__":
    main()
