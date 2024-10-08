import requests
import os
import pandas as pd

# Replace with your GraphQL endpoint and set up the API token as an env variable
OPSLEVEL_API_TOKEN = os.environ["OPSLEVEL_API_TOKEN"]
url = 'https://api.opslevel.com/graphql'
headers = {
    'Authorization':  f"Bearer {API_TOKEN}",
    'Content-Type': 'application/json',
    'Graphql-Visibility': 'internal'
}

# GraphQL query to fetch services
query = """
query getServices($first: Int, $after: String) {
  account {
    allServices(first: $first, after: $after, sortBy: name_ASC) {
        pageInfo {
            endCursor
            hasNextPage
        }
        nodes {
            id
            name
            timestamps {
                updatedAt
            }        
        }
    }
  }
}
"""
def fetch_services():
    services = []
    has_next_page = True
    after = None

    while has_next_page:
        variables = {
            "first": 100,  # Number of items to fetch per request
            "after": after
        }

        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
        print(response.json())
        if response.status_code == 200:
            data = response.json()['data']['account']['allServices']
            services.extend(data['nodes'])
            has_next_page = data['pageInfo']['hasNextPage']
            after = data['pageInfo']['endCursor']
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    return services

# Fetch the services
services = fetch_services()

# Extract id and name
service_data = [(service['id'], service['name'], service['timestamps']['updatedAt']) for service in services]

# Create a DataFrame
df = pd.DataFrame(service_data, columns=['id', 'name', 'updatedAt'])

# Save to CSV
csv_path = 'services_graphqlapi.csv'
df.to_csv(csv_path, index=False)
print(f"CSV file has been created at {csv_path}")