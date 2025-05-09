import os
import requests
import json

OPSLEVEL_API_TOKEN = os.environ["OPSLEVEL_API_TOKEN"]
OPSLEVEL_ENDPOINT = "https://app.opslevel.com/graphql"

LIST_COMPONENT_TYPES_QUERY = """
    query componentTypes($endCursor: String) {
      account {
        componentTypes (after: $endCursor) {
          nodes {
            id
            name
          }
          pageInfo {
            endCursor
            hasNextPage
          }
        }
      }
    }
"""

LIST_COMPONENT_TYPE_PROPERTIES_QUERY = """
    query componentTypes_properties($componentTypeID: ID, $componentTypeAlias: String, $endCursor: String) {
      account {
        componentType(input: {id: $componentTypeID, alias: $componentTypeAlias}) {
          id
          name
          properties(after: $endCursor) {
            nodes {
              id
              name
              alias
              schema
              description
              lockedStatus
              propertyDisplayStatus
              allowedInConfigFiles
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
      }
   }
"""

PROPERTY_DEFINIITION_CREATE_MUTATION = """
    mutation propertyDefinitionCreate($componentTypeID:ID, $componentTypeAlias:String, $properties:[ComponentTypePropertyDefinitionInput!]){
      componentTypeUpdate(componentType: {id: $componentTypeID, alias:$componentTypeAlias}, input:{properties:$properties}){
        componentType{
          id
          name
          properties{
            nodes{
              id
              name
              alias
              schema
              description
              lockedStatus
              propertyDisplayStatus
              allowedInConfigFiles
            }
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
    return response.json()

def fetch_component_types():
    """
    Fetches all component types from OpsLevel
    """
    cursor = None
    has_next_page = True
    component_types = []  # Store fetched component types
    while has_next_page:
        response = opslevel_graphql_query(
            LIST_COMPONENT_TYPES_QUERY, variables={"endCursor": cursor}
        )
        nodes = response["data"]["account"]["componentTypes"]["nodes"]
        component_types.extend(nodes)
        page_info = response["data"]["account"]["componentTypes"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

    return component_types

def fetch_component_type_properties(component_type_id):
    cursor = None
    has_next_page = True
    properties = []
    while has_next_page:
        response = opslevel_graphql_query(
            LIST_COMPONENT_TYPE_PROPERTIES_QUERY,
            variables={"componentTypeID": component_type_id, "endCursor": cursor},
        )
        nodes = response["data"]["account"]["componentType"]["properties"]["nodes"]
        properties.extend(nodes)
        page_info = response["data"]["account"]["componentType"]["properties"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]
    return properties


def create_or_update_properties(component_type_id, properties):
    """
    Call the mutation to update properties on a component type
    """
    # Build input in the required format
    property_inputs = [
        {
            "name": prop["name"],
            "alias": prop["alias"],
            "schema": prop["schema"],
            "description": prop.get("description", ""),
            "lockedStatus": prop.get("lockedStatus", "UNLOCKED"),
            "propertyDisplayStatus": prop.get("propertyDisplayStatus", "VISIBLE"),
            "allowedInConfigFiles": prop.get("allowedInConfigFiles", True),
        }
        for prop in properties
    ]

    response = opslevel_graphql_query(
        PROPERTY_DEFINIITION_CREATE_MUTATION,
        variables={
            "componentTypeID": component_type_id,
            "properties": property_inputs,
        },
    )
    print("Properties updated successfully.")
    return response


def main():
    component_types = fetch_component_types()

    print("Select a component type to retrieve properties:")
    for i, component_type in enumerate(component_types):
        print(f"{i+1}. {component_type['name']} ({component_type['id']})")
    component_type_number = int(input("Enter the number: ")) - 1
    source_component_type = component_types[component_type_number]
    source_component_type_id = source_component_type["id"]

    source_properties = fetch_component_type_properties(source_component_type_id)

    print("\nSelect a property to copy to another component type (or enter 'a' to copy all):")
    for i, property in enumerate(source_properties):
        print(f"{i+1}. {property['name']} ({property['id']})")
    action = input("> ").lower()
    if action == "a":
        properties_to_copy = source_properties
    else:
        property_number = int(action) - 1
        properties_to_copy = [source_properties[property_number]]

    print("\nSelect a component type to copy the property to:")
    for i, component_type in enumerate(component_types):
        print(f"{i+1}. {component_type['name']} ({component_type['id']})")
    copy_to_component_type_number = int(input("Enter the number: ")) - 1
    dest_component_type = component_types[copy_to_component_type_number]
    dest_component_type_id = dest_component_type["id"]

    # Fetch existing properties of the destination
    dest_properties = fetch_component_type_properties(dest_component_type_id)

    # Merge, avoiding duplicates by alias
    existing_aliases = {prop["alias"] for prop in dest_properties}
    new_properties = [prop for prop in properties_to_copy if prop["alias"] not in existing_aliases]
    all_properties = dest_properties + new_properties

    # Update destination with merged properties
    create_or_update_properties(dest_component_type_id, all_properties)


if __name__ == "__main__":
    if not OPSLEVEL_API_TOKEN:
        raise ValueError("OPSLEVEL_API_TOKEN environment variable is not set.")
    main()