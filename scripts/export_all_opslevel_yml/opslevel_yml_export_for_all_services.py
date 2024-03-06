import os
import requests

OPSLEVEL_API_TOKEN = os.environ["OPSLEVEL_API_TOKEN"]
OPSLEVEL_ENDPOINT = "https://app.opslevel.com/graphql"


# Function to make a GraphQL query
def opslevel_graphql_query(query, variables=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPSLEVEL_API_TOKEN}",
    }
    data = {"query": query, "variables": variables}
    response = requests.post(OPSLEVEL_ENDPOINT, json=data, headers=headers)
    return response.json()


# Main function to execute the script
def main():

    # Define your GraphQL queries
    list_services_query = """
        query get_services($endCursor:String){
        account{
            services(after: $endCursor){
            nodes{
                name
                id
            }
            pageInfo{
                hasNextPage
                endCursor
            }
            }
        }
        }
    """

    fetch_opslevel_yml_for_service = """
        query get_opslevel_yml($id:ID!) {
        account {
            configFile(id:$id) {
            ownerType
            yaml
            }
        }
        }
    """

    # Make the first GraphQL query to get a list of items with pagination
    cursor = None
    has_next_page = True
    while has_next_page:
        response_1 = opslevel_graphql_query(
            list_services_query, variables={"cursor": cursor}
        )
        nodes = response_1["data"]["account"]["services"]["nodes"]
        for node in nodes:
            service_id = node["id"]
            service_name = node["name"]
            variables = {"id": service_id}
            # Make the second GraphQL query to get the yaml for each service
            response_2 = opslevel_graphql_query(
                fetch_opslevel_yml_for_service, variables
            )
            yaml_data = response_2["data"]["account"]["configFile"]["yaml"]
            filename = f"{service_name}_opslevel.yml"
            with open(filename, "a") as f:
                f.write(yaml_data)

        has_next_page = response_1["data"]["account"]["services"]["pageInfo"]["hasNextPage"]
        cursor = response_1["data"]["account"]["services"]["pageInfo"]["endCursor"]


if __name__ == "__main__":
    main()
