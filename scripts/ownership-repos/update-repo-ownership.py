import json
import requests
import sys
import argparse
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURATION ---
API_TOKEN = os.getenv("OPSLEVEL_API_TOKEN")

if not API_TOKEN:
    print("Error: 'OPSLEVEL_API_TOKEN' environment variable is not set.")
    sys.exit(1)

API_URL = "https://api.opslevel.com/graphql"
# Changed to relative path for portability, or use CLI arg
DEFAULT_INPUT_FILE = "/Users/tomszacharia/code/customers/tavisca/ownership-repos/repos.json" 

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# --- GRAPHQL DEFINITIONS ---

GET_ALL_REPOS_QUERY = """
query get_all_repository_ids($after: String) {
  account {
    repositories(after: $after) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        id
        name
        defaultAlias
      }
    }
  }
}
"""

# UPDATED: Get ALL Teams (No search term, just paginated list)
GET_ALL_TEAMS_QUERY = """
query get_all_teams($after: String) {
  account {
    teams(after: $after) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        id
        name
        aliases
      }
    }
  }
}
"""

CREATE_TEAM_MUTATION = """
mutation create_team($name:String!) {
  teamCreate(input: {name: $name}) {
    team {
      id
      name
    }
    errors {
      message
    }
  }
}
"""

UPDATE_REPO_MUTATION = """
mutation repoOwnerUpdate($id: ID!, $ownerId: ID, $syncLinkedServices: Boolean) {
  repositoryUpdate(
    input: {id: $id, ownerId: $ownerId}
    syncLinkedServices: $syncLinkedServices
  ) {
    repository {
      id
      owner {
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

# --- SESSION SETUP (Retry Logic) ---
def get_requests_session():
    """Creates a session with retry logic for 429s and 5xx errors."""
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=1, # Sleep 1s, 2s, 4s...
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

# Global session
http = get_requests_session()

# --- HELPER FUNCTIONS ---

def run_query(query_name, query, variables=None):
    """Runs GraphQL with error handling for both HTTP and GraphQL-level errors."""
    try:
        response = http.post(API_URL, json={'query': query, 'variables': variables}, headers=headers)
        response.raise_for_status() # Raises error for 4xx/5xx
        
        result = response.json()
        
        # Check for GraphQL Logic Errors (Top level)
        if "errors" in result:
            # We log it, but we return the result so the caller can decide 
            # if it's fatal or if they want to parse the specific error message
            print(f"   [!] GraphQL Error in {query_name}: {result['errors'][0]['message']}")
            
        return result
    except requests.exceptions.RequestException as e:
        print(f"   [!!!] Critical Network Error in {query_name}: {e}")
        sys.exit(1) # Exit immediately on network failure after retries

def fetch_paginated_data(entity_name, query, extraction_path):
    """
    Generic function to fetch all pages of a resource.
    extraction_path: keys to traverse to get nodes e.g. ['account', 'repositories']
    """
    print(f"Fetching all {entity_name} from OpsLevel...")
    
    entity_map = {} # Key: Name, Value: ID
    has_next_page = True
    cursor = None
    
    while has_next_page:
        variables = {"after": cursor}
        result = run_query(f"Fetch {entity_name}", query, variables)
        
        # Safety: Handle if data is None
        data = result.get("data")
        if not data:
            print(f"Error: No data returned for {entity_name}")
            break

        # Traverse the path (e.g. data['account']['repositories'])
        current_level = data
        for key in extraction_path:
            current_level = current_level.get(key, {})
            
        nodes = current_level.get("nodes", [])
        page_info = current_level.get("pageInfo", {})

        for node in nodes:
            # Standardize keys to lowercase for case-insensitive lookup
            entity_map[node['name'].lower()] = node['id']
            
            # OPTIONAL: Map aliases to ID as well if you want to match on alias
            # for alias in node.get('aliases', []):
            #     entity_map[alias.lower()] = node['id']

        has_next_page = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")
        print(".", end="", flush=True)

    print(f"\nTotal {entity_name} found: {len(entity_map)}")
    return entity_map

def create_new_team(squad_name):
    print(f"   [+] Creating Team '{squad_name}'...")
    variables = {"name": squad_name}
    data = run_query("Create Team", CREATE_TEAM_MUTATION, variables)
    
    # Robust check for deeply nested errors
    result = data.get("data", {}).get("teamCreate", {})
    if not result:
         return None

    errors = result.get("errors", [])
    if errors:
        print(f"   [!] Failed to create team: {errors}")
        return None
        
    return result.get("team", {}).get("id")

def update_repo_owner(repo_id, team_id, repo_name, squad_name):
    variables = {
        "id": repo_id,
        "ownerId": team_id,
        "syncLinkedServices": True
    }
    
    data = run_query("Update Owner", UPDATE_REPO_MUTATION, variables)
    
    # Robust check
    res_data = data.get("data")
    if not res_data: return

    result = res_data.get("repositoryUpdate", {})
    errors = result.get("errors", [])
    
    if errors:
        print(f"   [!] Error updating {repo_name}: {errors[0]['message']}")
    else:
        print(f"   [✓] Updated '{repo_name}' owner to '{squad_name}'")

# --- MAIN EXECUTION ---

def main():
    parser = argparse.ArgumentParser(description="Update OpsLevel Repo Ownership")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution")
    parser.add_argument("--file", default=DEFAULT_INPUT_FILE, help="Path to input JSON file")
    args = parser.parse_args()

    if args.dry_run:
        print("\n*** DRY RUN MODE ***\n")

    # 1. Load Input
    if not os.path.exists(args.file):
        print(f"Error: Input file '{args.file}' not found.")
        sys.exit(1)

    with open(args.file, 'r') as f:
        try:
            payload = json.load(f)
        except json.JSONDecodeError:
            print("Error: Invalid JSON file.")
            sys.exit(1)

    repos_input = payload.get("repositories", [])
    print(f"Input loaded: {len(repos_input)} repositories to process.\n")

    # 2. PRE-FETCH EVERYTHING (Optimization: O(1) lookup later)
    # Fetch Repos
    opslevel_repos = fetch_paginated_data(
        "Repositories", 
        GET_ALL_REPOS_QUERY, 
        ['account', 'repositories']
    )
    
    # Fetch Teams (New Optimization)
    opslevel_teams = fetch_paginated_data(
        "Teams", 
        GET_ALL_TEAMS_QUERY, 
        ['account', 'teams']
    )

    # 3. Process
    summary = {
        "repos_found": [], "repos_not_found": [],
        "teams_found": [], "teams_created": [] 
    }

    print("\n--- Starting Processing ---")

    for entry in repos_input:
        repo_name = entry.get("name")
        squad_name = entry.get("squadName")
        
        # Use lowercase for reliable lookup
        repo_key = repo_name.lower()
        squad_key = squad_name.lower()

        # A. Check Repo Exists
        repo_id = opslevel_repos.get(repo_key)
        if not repo_id:
            print(f"Skip: Repo '{repo_name}' not found in OpsLevel.")
            summary["repos_not_found"].append(repo_name)
            continue
        summary["repos_found"].append(repo_name)

        # B. Check Team Exists
        team_id = opslevel_teams.get(squad_key)

        # C. Create Team if Missing
        if not team_id:
            if args.dry_run:
                print(f"   [DRY RUN] Would create team '{squad_name}'")
                summary["teams_created"].append(squad_name)
                team_id = "mock_id"
            else:
                new_id = create_new_team(squad_name)
                if new_id:
                    team_id = new_id
                    # Add to local cache so we don't try to create it again in this loop
                    opslevel_teams[squad_key] = new_id 
                    summary["teams_created"].append(squad_name)
                else:
                    print("   [!] Skipping update due to team creation failure.")
                    continue
        else:
            # Track unique teams found
            if squad_name not in summary["teams_found"]:
                summary["teams_found"].append(squad_name)

        # D. Update Ownership
        if args.dry_run:
            print(f"   [DRY RUN] Would assign '{repo_name}' to '{squad_name}'")
        else:
            update_repo_owner(repo_id, team_id, repo_name, squad_name)

    # --- SUMMARY ---
    print(f"\nSummary: Found {len(summary['repos_found'])} Repos, Missing {len(summary['repos_not_found'])}.")
    print(f"Teams Found: {len(summary['teams_found'])}, Created: {len(summary['teams_created'])}.")

if __name__ == "__main__":
    main()