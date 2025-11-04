"""
get_wiz_vulnerabilities.py

Description:
    This script pulls all vulnerability findings from your Wiz environment using GraphQL.

Dependencies:
    - Python 3.8+
    - requests==2.28.2

Usage:
    export WIZ_CLIENT_ID="<your_client_id>"
    export WIZ_CLIENT_SECRET="<your_client_secret>"
    export WIZ_API_ENDPOINT="https://api.us87.app.wiz.io/graphql"
    export WIZ_TOKEN_URL="https://auth.app.wiz.io/oauth/token"

    python3 get_wiz_vulnerabilities.py
"""

import os
import json
import time
import requests
from typing import Dict, List, Any, Optional

# --- Constants ---
AUTH0_URLS = [
    'https://auth.wiz.io/oauth/token',
    'https://auth0.gov.wiz.io/oauth/token',
    'https://auth0.test.wiz.io/oauth/token',
    'https://auth0.demo.wiz.io/oauth/token'
]
COGNITO_URLS = [
    'https://auth.app.wiz.io/oauth/token',
    'https://auth.gov.wiz.io/oauth/token',
    'https://auth.test.wiz.io/oauth/token',
    'https://auth.demo.wiz.io/oauth/token'
]

HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

# --- GraphQL Query ---
WIZ_QUERY = """
query VulnerabilityFindingsPage($filterBy: VulnerabilityFindingFilters, $first: Int, $after: String) {
  vulnerabilityFindings(
    filterBy: $filterBy
    first: $first
    after: $after
    orderBy: {direction: DESC}
  ) {
    nodes {
      id
      name
      portalUrl
      CVEDescription
      CVSSSeverity
      score
      status
      firstDetectedAt
      lastDetectedAt
      resolvedAt
      remediation
      vulnerableAsset {
        ... on VulnerableAssetBase {
          id
          type
          name
          region
          tags
          cloudPlatform
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

# --- Functions ---
def get_env_variable(var_name: str) -> str:
    """Fetch an environment variable or raise an error."""
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value


def request_wiz_api_token(client_id: str, client_secret: str, token_url: str) -> str:
    """Retrieve an OAuth access token from Wiz."""
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
        raise ValueError(f"Invalid token URL: {token_url}")

    response = requests.post(url=token_url, headers=HEADERS_AUTH, data=auth_payload)
    if response.status_code != 200:
        raise Exception(f"Error authenticating to Wiz [{response.status_code}] - {response.text}")

    token = response.json().get('access_token')
    if not token:
        raise Exception(f"Could not retrieve token from Wiz: {response.text}")

    HEADERS["Authorization"] = f"Bearer {token}"
    return token


def query_wiz_api(query: str, variables: Dict[str, Any], endpoint_url: str) -> Dict[str, Any]:
    """Perform a GraphQL query against the Wiz API."""
    for attempt in range(3):  # Retry up to 3 times on transient errors
        try:
            response = requests.post(url=endpoint_url, json={"query": query, "variables": variables}, headers=HEADERS)
            if response.status_code == 200:
                return response.json()
            elif response.status_code >= 500:
                print(f"Server error {response.status_code}, retrying ({attempt + 1}/3)...")
                time.sleep(2)
            else:
                print(f"Error {response.status_code}: {response.text}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}, retrying...")
            time.sleep(2)
    return {}


def fetch_all_vulnerabilities(endpoint_url: str) -> List[Dict[str, Any]]:
    """Fetch all vulnerability findings using pagination."""
    vulnerabilities = []
    variables = {"first": 200, "filterBy": {}, "after": None}

    while True:
        data = query_wiz_api(WIZ_QUERY, variables, endpoint_url)
        if not data or "data" not in data or "vulnerabilityFindings" not in data["data"]:
            print("No data returned or invalid response format.")
            break

        findings = data["data"]["vulnerabilityFindings"]["nodes"]
        page_info = data["data"]["vulnerabilityFindings"]["pageInfo"]

        for node in findings:
            try:
                vulnerabilities.append({
                    "id": node["id"],
                    "name": node.get("name"),
                    "severity": node.get("CVSSSeverity"),
                    "score": node.get("score"),
                    "status": node.get("status"),
                    "portal_url": node.get("portalUrl"),
                    "first_detected_at": node.get("firstDetectedAt"),
                    "vulnerable_asset_type": node["vulnerableAsset"]["type"] if node.get("vulnerableAsset") else None,
                    "tags": node["vulnerableAsset"].get("tags") if node.get("vulnerableAsset") else None,
                })
            except Exception as e:
                print(f"Error parsing node: {e}")

        if not page_info.get("hasNextPage"):
            break
        variables["after"] = page_info.get("endCursor")

    return vulnerabilities


def main():
    print("Starting Wiz vulnerability extraction...")
    try:
        client_id = get_env_variable("WIZ_CLIENT_ID")
        client_secret = get_env_variable("WIZ_CLIENT_SECRET")
        endpoint_url = get_env_variable("WIZ_API_ENDPOINT")
        token_url = get_env_variable("WIZ_TOKEN_URL")

        print("Authenticating to Wiz...")
        request_wiz_api_token(client_id, client_secret, token_url)

        print("Fetching vulnerability findings...")
        vulnerabilities = fetch_all_vulnerabilities(endpoint_url)

        print(f"✅ Extracted {len(vulnerabilities)} vulnerabilities.")
        print(json.dumps(vulnerabilities[:5], indent=2))  # Show sample

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()