import subprocess
import json
import os
import datetime

# Define the GraphQL queries
OL_SERVICES_QUERY = """
query get_all_systems($endCursor: String) {
  account {
    systems(after: $endCursor) {
      nodes {
        id
        name
        description
        aliases
        managedAliases
        owner {
          ... on Team {
            id
            name
            alias
          }
        }
        tags {
          nodes {
            id
            key
            value
          }
        }
        parent {
          id
          name
        }
        childServices {
          nodes {
            id
            name
          }
        }
        childInfrastructureResources {
          nodes {
            id
            name
          }
        }
        note
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

OL_SERVICE_MUTATION = """
mutation service_create($alias: String!, $description: String, $ownerInput: IdentifierInput) {
  serviceCreate(
    input: {name: $alias, description: $description, ownerInput: $ownerInput}
  ) {
    service {
      id
      name
      description
      aliases
      htmlUrl
      owner {
        alias
      }
      tier {
        alias
      }
      tags {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          key
          value
        }
      }
    }
    errors {
      message
      path
    }
  }
}
"""

OL_SERVICE_TO_SERVICE_DEPENDENCIES_MUTATION = """
mutation service_depends_on_service($searchServiceId: ID, $serviceId: ID) {
  serviceDependencyCreate(
    inputV2: {dependencyKey: {sourceIdentifier: {id: $searchServiceId}, destinationIdentifier: {id: $serviceId}}}
  ) {
    serviceDependency {
      id
      sourceService {
        id
        name
      }
      destinationService {
        id
        name
      }
    }
    errors {
      message
      path
    }
  }
}
"""

OL_SERVICE_TO_INFRASTRUCTURE_DEPENDENCIES_MUTATION = """
mutation infraRelationshipCreate($source: IdentifierInput!, $target: IdentifierInput!, $type: RelationshipTypeEnum!) {
  relationshipCreate(
    relationshipDefinition: {source: $source, target: $target, type: $type}
  ) {
    relationship {
      id
      type
      source {
        ... on Service {
          id
          name
          __typename
        }
        ... on System {
          id
          name
          __typename
        }
        ... on InfrastructureResource {
          id
          name
          __typename
        }
      }
      target {
        ... on Service {
          id
          name
          __typename
        }
        ... on System {
          id
          name
          __typename
        }
        ... on Domain {
          id
          name
          __typename
        }
        ... on InfrastructureResource {
          id
          name
          __typename
        }
      }
    }
    errors {
      message
      path
    }
  }
}

"""

# Get the API token from environment variables
OPSLEVEL_API_TOKEN = os.environ.get("OPSLEVEL_API_TOKEN")

if not OPSLEVEL_API_TOKEN:
    raise EnvironmentError("OPSLEVEL_API_TOKEN environment variable not set")

# The command to execute the query
command = [
    "opslevel", 
    "graphql", 
    f"--api-token={OPSLEVEL_API_TOKEN}", 
    "--paginate", 
    "-a=.account.systems.nodes[]", 
    f"-q={OL_SERVICES_QUERY}"
]

# Run the query and capture the output
try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    
    # The result's output contains the JSON response
    json_output = result.stdout

    # Load the JSON output into a Python variable
    data = json.loads(json_output)
    
    print("GraphQL query executed successfully and data captured.")
    
except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error parsing JSON output: {e}")
    exit(1)

# Presenting options to the user as a list
print("\nPlease choose one of the following options:")
print("1. Back up the data to a file.")
print("2. Run a mutation based on this data.")
print("3. Exit.")

# Ask the user to select an option
user_choice = input("Enter the number of your choice: ")

if user_choice == "1":
    # Back up the data to a file
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"systems_backup_{current_time}.json"

    # Write the data to a file
    try:
        with open(filename, "w") as backup_file:
            json.dump(data, backup_file, indent=4)
        print(f"Data successfully backed up to {filename}.")
    except IOError as e:
        print(f"Error writing backup file: {e}")
elif user_choice == "2":
    # Mutation logic: iterate through each item in `data`
    for system in data:
        alias = "SEARCH-" +system.get('name', '')
        description = system.get('description', '')
        
        # Extract owner information (handle if owner is None)
        owner = system.get('owner', {})
        owner_id = owner.get('id') if owner else None
        
        # Extract tags
        #tags_nodes = system.get('tags', {}).get('nodes', [])
        #tags = [{"key": tag["key"], "value": tag["value"]} for tag in tags_nodes]
        
        # Format tags into string representation for mutation input
        #formatted_tags = ','.join([f'{tag["key"]}:{tag["value"]}' for tag in tags])

        # Prepare the mutation command in -f key=value format
        mutation_command = [
            "opslevel",
            "graphql",
            f"--api-token={OPSLEVEL_API_TOKEN}",
            "-f", f"alias={alias}",
            "-f", f"description={description}",
            "-f", f"ownerId={owner_id}" if owner_id else "-f ownerId=null",
            #"-f", f"tags={formatted_tags}" if formatted_tags else "-f tags=[]",
            f"-q={OL_SERVICE_MUTATION}"
        ]

        # Execute the mutation
        try:
            mutation_result = subprocess.run(mutation_command, capture_output=True, text=True, check=True)
            print(f"Mutation for {alias} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing mutation for {alias}: {e}")
elif user_choice == "3":
    print("Exiting the program.")
else:
    print("Invalid choice. Please run the program again and select a valid option.")
