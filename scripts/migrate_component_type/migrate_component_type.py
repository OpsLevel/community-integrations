import requests
import argparse
import sys

# --- GraphQL Definitions ---

# 1. Query to fetch Services, including pagination cursor
GET_SERVICES_QUERY = """
query getServicesByTags ($filter: [ServiceFilterInput!], $after: String) {
  account {
    services (filter: $filter, after: $after) {
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

# 2. Mutation to update a Service's type
UPDATE_SERVICE_MUTATION = """
mutation updateService($id: ID!, $type: IdentifierInput) {
  serviceUpdate(input: {id: $id, type: $type}) {
    service {
      name
      id
    }
    errors {
      path
      message
    }
  }
}
"""

def parse_arguments():
    """Parses command line arguments for configuration."""
    parser = argparse.ArgumentParser(
        description="Bulk update OpsLevel Service Component Types based on a tag filter."
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Your OpsLevel API Token (e.g., opsl_xxx...)."
    )
    parser.add_argument(
        "--target-type-id",
        required=True,
        help="The OpsLevel ID of the new Component Type to assign to matching services (e.g., Z2lkOi8vb3BzbGV2ZWwvQ29tcG9uZW50VHlwZXM6OlNlcnZpY2UvMTEwNQ)."
    )
    # New argument for filtering by the service's current component type ID
    parser.add_argument(
        "--source-type-id-filter",
        required=True,
        help="The OpsLevel ID of the Component Type to filter services by (e.g., Z2lkOi8vb3BzbGV2ZWwvQ29tcG9uZW50VHlwZXM6OlNlcnZpY2UvNTE4). Only services matching this type will be considered for the update."
    )
    parser.add_argument(
        "--tag-arg",
        required=True,
        help="The specific tag value to filter by (e.g., 'role:http')."
    )
    parser.add_argument(
        "--tag-key",
        default="tag",
        help="The key to use for filtering (usually 'tag' for OpsLevel tags)."
    )
    parser.add_argument(
        "--api-url",
        default="https://api.opslevel.com/graphql",
        help="The OpsLevel GraphQL API endpoint URL."
    )
    return parser.parse_args()

def execute_graphql(api_url, token, query, variables):
    """Executes a GraphQL request and handles basic HTTP errors."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "graphql-visibility": "internal"  # Added new header
    }
    payload = {"query": query, "variables": variables}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error executing GraphQL request: {e}")
        sys.exit(1)


def get_all_services(args):
    """Fetches all services matching the combined filters, handling pagination."""
    all_services = []
    cursor = None
    has_next = True

    # Construct the array of filters combining component type ID and tag
    filters = [
        {
            "key": "component_type_id",
            "arg": args.source_type_id_filter,
            "type": "equals"
        },
        {
            "key": args.tag_key,
            "arg": args.tag_arg,
            "type": "equals"
        },
                {
            "key": args.tag_key_1,
            "arg": args.tag_arg_1,
            "type": "does_not_equal"
        }
    ]
    
    print(f"Fetching services with filters: component_type_id={args.source_type_id_filter} AND {args.tag_key}={args.tag_arg}...")

    while has_next:
        variables = {
            "filter": filters, # Use the combined filters array
            "after": cursor
        }
        
        result = execute_graphql(args.api_url, args.token, GET_SERVICES_QUERY, variables)

        # Check for GraphQL errors (e.g., invalid token)
        if 'errors' in result:
             print("GraphQL Errors encountered during service fetching:")
             for error in result['errors']:
                 print(f"  - {error.get('message', 'Unknown Error')}")
             sys.exit(1)

        service_data = result['data']['account']['services']
        all_services.extend(service_data['nodes'])

        page_info = service_data['pageInfo']
        has_next = page_info['hasNextPage']
        cursor = page_info['endCursor']
        
        if has_next:
            print(f"  - Fetching next page, current total: {len(all_services)}")

    print(f"Found a total of {len(all_services)} services to update.")
    return all_services

def update_service_type(args, service_id):
    """Mutates a single service to the new component type."""
    variables = {
        "id": service_id,
        "type": {"id": args.target_type_id}
    }
    return execute_graphql(args.api_url, args.token, UPDATE_SERVICE_MUTATION, variables)

def main():
    """Main execution function."""
    args = parse_arguments()
    
    services_to_update = get_all_services(args)

    if not services_to_update:
        print("No services found matching the filter. Script finished.")
        return

    print(f"\nStarting update for {len(services_to_update)} services to new Component Type ID: {args.target_type_id}")
    
    success_count = 0
    failure_count = 0

    for service in services_to_update:
        service_name = service['name']
        service_id = service['id']
        
        try:
            print(f"  -> Updating {service_name}...", end=' ')
            result = update_service_type(args, service_id)
            
            update_result = result['data']['serviceUpdate']
            
            if update_result['errors']:
                error_msgs = [e['message'] for e in update_result['errors']]
                print(f"**FAILED**: {', '.join(error_msgs)}")
                failure_count += 1
            else:
                print("**SUCCESS**")
                success_count += 1
                
        except Exception as e:
            print(f"An unexpected error occurred for {service_name}: {e}")
            failure_count += 1
        
        # Exit after the first iteration as requested
        # print("Stopping after the first service.")
        # break
            
    print("\n--- Summary ---")
    print(f"Total Services Processed: {success_count + failure_count}")
    print(f"Successfully Updated: {success_count}")
    print(f"Failed to Update: {failure_count}")


if __name__ == "__main__":
    main()