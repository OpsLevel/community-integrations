import os
import requests
import json

OPSLEVEL_API_TOKEN = os.environ["OPSLEVEL_API_TOKEN"]
OPSLEVEL_ENDPOINT = "https://app.opslevel.com/graphql"

LIST_CUSTOM_PROPERTIES_QUERY = """
    query custom_service_properties($endCursor:String) {
      account {
        propertyDefinitions(after: $endCursor) {
          pageInfo{
            hasNextPage
            endCursor
          }
          nodes {
            name
            aliases
            schema
            id
          }
        }
      }
    }
"""

SERVICES_BY_TAG_QUERY = """
    query services_by_tag($endCursor: String, $tag_key:String){
      account{
        services(tag: {key: $tag_key}, after: $endCursor){
          pageInfo{
            hasNextPage
            endCursor
          }
          nodes{
            id
            tags{
              nodes{
                id
                key
                value
              }
            }
          }
        }
      }
    }
"""

UPDATE_PROPERTY_MUTATION = """
    mutation update_property($service_id:ID, $definition_alias:String, $value:JsonString!){
      propertyAssign(input: {owner: {id: $service_id}, definition: {alias: $definition_alias},
      value: $value, runValidation: false}) {
        property{
          value
          owner{
            ...on Service{
              name
            }
          }
        }
        errors{
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
    return response.json()


def fetch_custom_properties():
    """
    Fetch custom properties from OpsLevel and return a list of properties.
    """
    cursor = None
    has_next_page = True
    properties = []  # Store fetched properties
    while has_next_page:
        response = opslevel_graphql_query(
            LIST_CUSTOM_PROPERTIES_QUERY, variables={"endCursor": cursor}
        )
        nodes = response["data"]["account"]["propertyDefinitions"]["nodes"]
        properties.extend(nodes)
        page_info = response["data"]["account"]["propertyDefinitions"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

    return properties


def main():
    properties = fetch_custom_properties()

    for index, property_info in enumerate(properties, 1):
        property_name = property_info["name"]
        property_alias = property_info["aliases"][0]  # Only the first alias
        property_schema_type = property_info["schema"]["type"]
        print(f"{index}. Property Name: {property_name}, Alias: {property_alias}, Schema Type: {property_schema_type}")

    selected_index = int(input("Select a property by entering its index: ")) - 1
    if 0 <= selected_index < len(properties):
        selected_property = properties[selected_index]
        print(f"You selected: {selected_property['name']} with alias: {selected_property['aliases'][0]} and schema type: {selected_property['schema']['type']}")

        service_mutations = {
            "boolean": execute_boolean_mutation,
            "array": execute_array_mutation,
            "text": execute_text_mutation,
            "object": execute_object_mutation
        }

        mutation_executor = service_mutations.get(selected_property["schema"]["type"])
        if mutation_executor:
            mutation_executor(selected_property)
        else:
            print("Unsupported schema type.")


def execute_boolean_mutation(property_info):
    """
    Execute mutation for boolean schema type.
    """
    cursor = None
    while True:
        # Execute the GraphQL query using the selected alias as the tag key
        response_services_by_tag = opslevel_graphql_query(
            SERVICES_BY_TAG_QUERY, variables={"endCursor": cursor, "tag_key": property_info["aliases"][0]}
        )

        # Loop through the service nodes to confirm the key in tags nodes matches the selected alias
        services = response_services_by_tag["data"]["account"]["services"]["nodes"]
        for service in services:
            tags = service["tags"]["nodes"]
            for tag in tags:
                if tag["key"] == property_info["aliases"][0]:
                    print(f"Service ID: {service['id']} has the selected alias as a tag.")
                    # Execute the mutation query
                    response = opslevel_graphql_query(
                        UPDATE_PROPERTY_MUTATION,
                        variables={"service_id": service["id"], "definition_alias": property_info["aliases"][0], "value": tag["value"]}
                    )
                    # # Process the mutation response if needed
                    print("Bool mutation executed.")
                    print(response)
        else:
            print("No service found with the selected alias as a tag.")

        # Check if there are more pages
        if not response_services_by_tag["data"]["account"]["services"]["pageInfo"]["hasNextPage"]:
            break
        cursor = response_services_by_tag["data"]["account"]["services"]["pageInfo"]["endCursor"]


def execute_array_mutation(property_info):
    # Execute the GraphQL query using the selected alias as the tag key
    response_services_by_tag = opslevel_graphql_query(
        SERVICES_BY_TAG_QUERY, variables={"endCursor": None, "tag_key": property_info["aliases"][0]}
    )

    # Loop through the service nodes to confirm the key in tags nodes matches the selected alias
    services = response_services_by_tag["data"]["account"]["services"]["nodes"]
    for service in services:
        tags = service["tags"]["nodes"]
        array_values = [tag_node["value"] for tag_node in tags if tag_node["key"] == property_info["aliases"][0]]
        # Convert array values to JSON string
        array_values_json = json.dumps(array_values)
        # Execute the mutation query
        response = opslevel_graphql_query(
            UPDATE_PROPERTY_MUTATION,
            variables={"service_id": service["id"], "definition_alias": property_info["aliases"][0], "value": array_values_json}
        )
        # Process the mutation response if needed
        print("Array mutation executed.")
        print(response)


def execute_text_mutation(property_info):
    """
    Execute mutation for text schema type.
    """
    # Implement text mutation logic here
    print("Running mutation for text schema type...")


def execute_object_mutation(property_info):
    """
    Execute mutation for object schema type.
    """
    # Implement object mutation logic here
    print("Running mutation for object schema type...")


if __name__ == "__main__":
    if OPSLEVEL_API_TOKEN is None:
        raise ValueError("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()
