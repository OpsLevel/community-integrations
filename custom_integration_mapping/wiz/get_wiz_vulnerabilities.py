"""
README
------
Description: This script pulls all vulnerabilities findings in your Wiz environment according to your arguments.
Dependencies: Python 3.7+, requests==2.28.2
How to use the script:
    The script has 4 required arguments:
    1) client_id
    2) client_secret
    3) api_endpoint
    4) token_url
"""


# Python 3.7+
# pip(3) install requests
import requests
import json
import os
from typing import Dict, List, Optional, Any


# Global variables
AUTH0_URLS = ['https://auth.wiz.io/oauth/token', 'https://auth0.gov.wiz.io/oauth/token', 'https://auth0.test.wiz.io/oauth/token', 'https://auth0.demo.wiz.io/oauth/token']
COGNITO_URLS = ['https://auth.app.wiz.io/oauth/token', 'https://auth.gov.wiz.io/oauth/token', 'https://auth.test.wiz.io/oauth/token', 'https://auth.demo.wiz.io/oauth/token']


# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

client_id = "teafpesnwrh27couq6awj5oity6tlcio3scftz4gsbui24ej3mzxg" #"mlipebtwsndhxdmnzdwrxzmiolmimcbbw2pv72mnuos335ktf4ohg"
client_secret = "GoZEX5AZA2BHABTyA1vuiF79TN2YQ79TJgizMyiGWEmjQMYJWSxQamhPIWCdg9Y3" #"JHGvdcHJ6mKZv6auEdTUp4riBJsqs9SEQqktJ4FeW2ovZu9ElwkoPuG0X2CDt1lj"
endpoint_url = "https://api.us87.app.wiz.io/graphql" #"https://api.us17.app.wiz.io/graphql"
token_url = "https://auth.app.wiz.io/oauth/token"

# Uncomment the following section to define the proxies in your environment,
#   if necessary:
# http_proxy  = "http://"+user+":"+passw+"@x.x.x.x:abcd"
# https_proxy = "https://"+user+":"+passw+"@y.y.y.y:abcd"
# proxyDict = {
#     "http"  : http_proxy,
#     "https" : https_proxy
# }

# The GraphQL query that defines which data you wish to fetch.
wiz_query = ("""
    query VulnerabilityFindingsPage($filterBy: VulnerabilityFindingFilters, $first: Int, $after: String) {
      vulnerabilityFindings(
        filterBy: $filterBy
        first: $first
        after: $after
        orderBy: {direction: DESC}
      ) {
        nodes {
          dataSourceName
          id
          portalUrl
          name
          CVEDescription
          CVSSSeverity
          score
          exploitabilityScore
          impactScore
          hasExploit
          hasCisaKevExploit
          status
          vendorSeverity
          firstDetectedAt
          lastDetectedAt
          resolvedAt
          description
          remediation
          detailedName
          version
          fixedVersion
          detectionMethod
          link
          locationPath
          resolutionReason
          projects {
            id
            name
            slug
            businessUnit
            riskProfile {
              businessImpact
            }
          }
          vulnerableAsset {
            ... on VulnerableAssetBase {
              id
              type
              name
              region
              providerUniqueId
              cloudProviderURL
              cloudPlatform
              status
              subscriptionName
              subscriptionExternalId
              subscriptionId
              tags
              hasLimitedInternetExposure
              hasWideInternetExposure
              isAccessibleFromVPN
              isAccessibleFromOtherVnets
              isAccessibleFromOtherSubscriptions
            }
            ... on VulnerableAssetVirtualMachine {
              operatingSystem
              ipAddresses
            }
            ... on VulnerableAssetServerless {
              runtime
            }
            ... on VulnerableAssetContainerImage {
              imageId
            }
            ... on VulnerableAssetContainer {
              ImageExternalId
              VmExternalId
              ServerlessContainer
              PodNamespace
              PodName
              NodeName
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
""")

# The variables sent along with the above query
variables = {
  "first": 5,
  "filterBy": {
      "relatedIssueSeverity": "MEDIUM"
  },
  "orderBy": {
  "field": "RELATED_ISSUE_SEVERITY",
  "direction": "DESC"
  }
}

def query_wiz_api(query, variables, endpoint_url):
    """Query WIZ API for the given query data schema"""
    data = {"variables": variables, "query": query}

    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # result = requests.post(url=endpoint_url,
        #                        json=data, headers=HEADERS, proxies=proxyDict)
        result = requests.post(url=endpoint_url,
                               json=data, headers=HEADERS)
        formatted_json = json.dumps(result.json(), indent=4)
        print(formatted_json)

    except Exception as e:
        if ('502: Bad Gateway' not in str(e) and
                '503: Service Unavailable' not in str(e) and
                '504: Gateway Timeout' not in str(e)):
            print("<p>Wiz-API-Error: %s</p>" % str(e))
            return(e)
        else:
            print("Retry")
    return result.json()

def request_wiz_api_token(client_id, client_secret, token_url):
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

    # Uncomment the next first line and comment the line after that
    # to run behind proxies
    # response = requests.post(url=token_url,
    #                         headers=HEADERS_AUTH, data=auth_payload,
    #                         proxies=proxyDict)
    response = requests.post(url=token_url,
                             headers=HEADERS_AUTH, data=auth_payload)

    if response.status_code != requests.codes.ok:
        raise Exception('Error authenticating to Wiz [%d] - %s' %
                        (response.status_code, response.text))

    try:
        response_json = response.json()
        TOKEN = response_json.get('access_token')
        if not TOKEN:
            message = 'Could not retrieve token from Wiz: {}'.format(
                    response_json.get("message"))
            raise Exception(message)
    except ValueError as exception:
        print(exception)
        raise Exception('Could not parse API response')
    HEADERS["Authorization"] = "Bearer " + TOKEN

    return TOKEN

def main():
    '''
    opslevel_token = os.environ.get("OPSLEVEL_API_TOKEN")
    if not opslevel_token:
        print("Error: OPSLEVEL_API_TOKEN environment variable not set.")
        return []  # Return an empty list
    '''    
    print("Getting Wiz token.")
    all_vulnerabilities = []
    request_wiz_api_token(client_id, client_secret, token_url)

    try: # added try catch
        response_data = query_wiz_api(wiz_query, variables, endpoint_url) # Call API
        #json_data = response_data.json()
        #print(json_data)
    except Exception as e:
        print(f"Error calling call_wiz_api: {e}")
        return []

    if response_data is None:
        return []  # Error occurred in the call_wiz_api function

    if "data" in response_data and "vulnerabilityFindings" in response_data["data"]:
        nodes = response_data["data"]["vulnerabilityFindings"]["nodes"]
        page_info = response_data["data"]["vulnerabilityFindings"]["pageInfo"]
        
        #print(page_info["endCursor"])

        for node in nodes:
            # only include nodes with tags
            #print(node["vulnerableAsset"])  
            extracted_data = {
                "name": node["name"],
                "cve_description": node["CVEDescription"],
                "first_detected_at": node["firstDetectedAt"],
                "severity": node["CVSSSeverity"],
                "portal_url": node["portalUrl"],
                "status": node["status"],
                "vulnerable_asset_type": node["vulnerableAsset"]["type"],
                "vulnerable_asset_tags": node["vulnerableAsset"]["tags"]
            }
            all_vulnerabilities.append(extracted_data)
        #print(all_vulnerabilities)
        print("Extracted all vulnerabilities. Count is: " + str(len(all_vulnerabilities)))

    else:
        print("Error: \'data\' or \'vulnerabilityFindings\' not found in response.")
        return []
    #print(all_vulnerabilities)    

if __name__ == '__main__':
    main()