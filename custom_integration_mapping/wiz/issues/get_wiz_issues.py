import requests
import json
import os
import sys
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone 

# --- Configuration ---
# Global authentication and endpoint URLs (used for validation/setup)
AUTH0_URLS = ['https://auth.wiz.io/oauth/token', 'https://auth0.gov.wiz.io/oauth/token', 'https://auth0.test.wiz.io/oauth/token', 'https://auth0.demo.wiz.io/oauth/token']
COGNITO_URLS = ['https://auth.app.wiz.io/oauth/token', 'https://auth.gov.wiz.io/oauth/token', 'https://auth.test.wiz.io/oauth/token', 'https://auth.demo.wiz.io/oauth/token']

# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

# Define page size for pagination
PAGE_SIZE = 50 

# --- OpsLevel Webhook Configuration (Configurable via Environment Variables) ---
OPSLEVEL_WEBHOOK_BASE_URL = "https://app.opslevel.com/integrations/custom/webhook/"
WEBHOOK_UID = os.getenv("OPSLEVEL_WEBHOOK_UID")
EXTERNAL_KIND = os.getenv("OPSLEVEL_EXTERNAL_KIND", "wiz_issues") 
# --------------------------------------------------------------------------

# --- Configuration File ---
CONFIG_FILE = "config.json"
# --------------------------

def get_config_path(file_name: str) -> str:
    """Calculates the absolute path to the configuration file relative to the script's directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, file_name)

def load_config(file_name: str) -> Dict[str, Any]:
    """
    Loads configuration settings from a local JSON file.
    """
    file_path = get_config_path(file_name)
    
    if not os.path.exists(file_path):
        print(f"Error: Configuration file '{file_path}' not found.")
        print("Please create it with the required 'status_changed_after' key, e.g., {'status_changed_after': '2024-01-01T00:00:00.000Z'}")
        return {}
    
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
            if 'status_changed_after' not in config:
                print(f"Error: '{file_name}' is missing the 'status_changed_after' key.")
                return {}
            return config
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'. Check file format.")
        return {}
    except IOError as e:
        print(f"Error reading configuration file '{file_path}': {e}")
        return {}

def update_config(file_name: str):
    """
    Updates the 'status_changed_after' key in the configuration file 
    to the current UTC timestamp (ISO 8601 format).
    """
    file_path = get_config_path(file_name)

    try:
        # Format: 2024-05-15T14:30:00.000Z
        new_timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Load the existing config (to preserve any other keys)
        config = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    pass # Ignore corruption, will overwrite timestamp

        # Update the timestamp
        config['status_changed_after'] = new_timestamp
        
        # Write the updated config back to the file
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"\nConfiguration file updated successfully. Next run will fetch issues changed after: {new_timestamp}")
        
    except Exception as e:
        print(f"\nWarning: Failed to update config file '{file_path}': {e}")

def send_to_webhook(data: List[Dict[str, Any]], webhook_uid: str, external_kind: str):
    """
    Sends the retrieved issue nodes for a single page to the OpsLevel webhook endpoint.
    """
    if not data:
        return

    webhook_url = f"{OPSLEVEL_WEBHOOK_BASE_URL}{webhook_uid}?external_kind={external_kind}"

    try:
        response = requests.post(
            webhook_url, 
            json=data, 
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print(f"Webhook: Successfully sent {len(data)} issues to UID '{webhook_uid}' with external_kind '{external_kind}'. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Webhook-Error: Failed to send data to OpsLevel: {e}")
        # Note: Implement retry logic or a dead-letter queue here if required.

def query_wiz_api(query: str, variables: dict, endpoint_url: str) -> Dict[str, Any]:
    """
    Query WIZ API for the given query data schema.
    """
    data = {"variables": variables, "query": query}

    try:
        result = requests.post(url=endpoint_url, json=data, headers=HEADERS)
        result.raise_for_status()
        
        response_json = result.json()

        if response_json.get("errors"):
            print("Wiz-API-Error: GraphQL Errors found in response:")
            print(json.dumps(response_json["errors"], indent=4))
            return {}
        
        return response_json

    except requests.exceptions.RequestException as e:
        print(f"Wiz-API-Error: Request failed - {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Wiz-API-Error: Failed to decode JSON response - {e}")
        return {}
    except Exception as e:
        print(f"Wiz-API-Error: An unexpected error occurred - {e}")
        return {}

def request_wiz_api_token(client_id: str, client_secret: str, token_url: str) -> str:
    """Retrieve an OAuth access token to be used against Wiz API"""
    if token_url in AUTH0_URLS:
        auth_payload = {
            'grant_type': 'client_credentials',
            'audience': 'beyond-api',
            'client_id': client_id,
            'client_secret': client_secret
        }
    elif token_url in COGNITO_URLS:
        auth_payload = {
            'grant_type': 'client_credentials',
            'audience': 'wiz-api',
            'client_id': client_id,
            'client_secret': client_secret
        }
    else:
        raise Exception('Invalid Token URL')

    try:
        response = requests.post(url=token_url, headers=HEADERS_AUTH, data=auth_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error authenticating to Wiz: {e}')

    try:
        response_json = response.json()
        TOKEN = response_json.get('access_token')
        if not TOKEN:
            message = 'Could not retrieve token from Wiz: {}'.format(
                    response_json.get("message", "Token field missing."))
            raise Exception(message)
    except ValueError:
        raise Exception('Could not parse API response for token')
    
    # Update global HEADDERS with the Authorization token
    HEADERS["Authorization"] = "Bearer " + TOKEN
    return TOKEN

def get_issues_query() -> str:
    """
    Returns the streamlined GraphQL query for fetching issues.
    Removed overly nested fields to optimize payload size.
    """
    # IMPROVEMENT 2: Streamlined query to fetch only essential data for OpsLevel Issue creation
    return """
        query IssuesTable($filterBy: IssueFilters, $first: Int, $after: String, $orderBy: IssueOrder) {
        issues: issuesV2(
            filterBy: $filterBy
            first: $first
            after: $after
            orderBy: $orderBy
        ) {
            nodes {
            id
            sourceRules {
                __typename
                ... on Control {
                id
                name
                controlDescription: description
                resolutionRecommendation
                # Removed deeply nested securitySubCategories, risks
                }
                ... on CloudEventRule {
                id
                name
                cloudEventRuleDescription: description
                sourceType
                type
                # Removed deeply nested securitySubCategories, risks
                }
                ... on CloudConfigurationRule {
                id
                name
                cloudConfigurationRuleDescription: description
                remediationInstructions
                serviceType
                # Removed deeply nested securitySubCategories, risks
                }
            }
            createdAt
            updatedAt
            dueAt
            type
            resolvedAt
            statusChangedAt
            # Retaining 'projects' but streamlined its fields
            projects {
                id
                name
                slug
                businessUnit
            }
            status
            severity
            # Retaining 'entitySnapshot' but streamlined its fields
            entitySnapshot {
                id
                type
                nativeType
                name
                status
                cloudPlatform
                cloudProviderURL
                providerId
                tags
                externalId
            }
            serviceTickets {
                externalId
                name
                url
            }
            }
            pageInfo {
            hasNextPage
            endCursor
            }
        }
        }
        """

def fetch_all_issues(query: str, initial_variables: Dict[str, Any], endpoint_url: str, webhook_uid: str, external_kind: str) -> int:
    """
    Fetches issues from the Wiz API using cursor-based pagination and sends each page 
    of results to the configured webhook.
    """
    total_issues_count = 0
    cursor = None
    has_next_page = True
    page_count = 0

    print(f"Starting to fetch issues with page size of {PAGE_SIZE} and send to webhook...")

    variables = initial_variables.copy()
    variables["first"] = PAGE_SIZE 

    while has_next_page:
        page_count += 1
        
        variables["after"] = cursor
        
        print(f"--- Fetching Page {page_count} (Cursor: {cursor or 'Start'}) ---")

        response_data = query_wiz_api(query, variables, endpoint_url)

        if not response_data or not response_data.get('data'):
            print("Received empty or malformed response data. Stopping pagination.")
            break
        
        issues_data = response_data['data']['issues']
        
        nodes = issues_data.get('nodes', [])
        
        # Pass webhook configuration to the send function
        if nodes:
            send_to_webhook(nodes, webhook_uid, external_kind)
        
        total_issues_count += len(nodes)
        print(f"-> Retrieved {len(nodes)} issues on this page. Total issues processed: {total_issues_count}")

        page_info = issues_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')

        if not has_next_page:
            break

    print("--- Pagination Complete ---")
    print(f"Total issues retrieved and sent to webhook: {total_issues_count}")
    return total_issues_count

def main():
    """
    Main function to execute the API call, handle pagination, and send to webhook.
    """
    print("Starting Wiz API script.")
    
    # IMPROVEMENT 1: Validate all required environment variables upfront
    client_id = os.getenv("WIZ_CLIENT_ID")
    client_secret = os.getenv("WIZ_CLIENT_SECRET")
    endpoint_url = os.getenv("WIZ_ENDPOINT_URL")
    token_url = os.getenv("WIZ_TOKEN_URL")
    webhook_uid = os.getenv("OPSLEVEL_WEBHOOK_UID")
    external_kind = os.getenv("OPSLEVEL_EXTERNAL_KIND") # Default is handled globally, but good to check

    required_vars = {
        "WIZ_CLIENT_ID": client_id,
        "WIZ_CLIENT_SECRET": client_secret,
        "WIZ_ENDPOINT_URL": endpoint_url,
        "WIZ_TOKEN_URL": token_url,
        "OPSLEVEL_WEBHOOK_UID": webhook_uid
    }

    missing_vars = [name for name, value in required_vars.items() if not value]
    if missing_vars:
        print(f"\n🛑 FATAL ERROR: The following required environment variables are missing: {', '.join(missing_vars)}")
        sys.exit(1)
        
    # 1. Authentication
    try:
        request_wiz_api_token(client_id, client_secret, token_url)
        print("Wiz token retrieved successfully.")
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    # 2. Load Configuration for Filters
    config = load_config(CONFIG_FILE)
    if not config:
        sys.exit(1)

    status_changed_after = config['status_changed_after']
    print(f"Filter configured to retrieve issues changed after: {status_changed_after}")
    
    # 3. Define Query and Initial Variables
    query = get_issues_query()
    
    base_variables = {
        "filterBy": {
            "severity": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            "statusChangedAt": {
                "after": status_changed_after
            }
        },
        "orderBy": {"field": "CREATED_AT", "direction": "DESC"}
    }

    # 4. Fetch All Issues with Pagination (and sending to webhook)
    total_issues_count = fetch_all_issues(
        query, 
        base_variables, 
        endpoint_url, 
        webhook_uid, 
        external_kind
    )
    
    # 5. Process Results
    if total_issues_count > 0:
        print(f"\n--- Script Finished ---")
        print(f"Successfully processed and sent {total_issues_count} issues to the OpsLevel webhook.")
        
        # SUCCESS: Update config file to current time
        update_config(CONFIG_FILE) 
        
    else:
        print("\nSuccessfully executed but no new issues were retrieved or processed.")
        sys.exit(0)

if __name__ == "__main__":
    main()