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

endpoint_url = "https://api.us17.app.wiz.io/graphql"
token_url = "https://auth.app.wiz.io/oauth/token"
integration_id = "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpDdXN0b21JbnRlZ3JhdGlvbi84OTcz"

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

def wiz_vulnerabilities_query():
    """
    Returns the GraphQL query and variables for fetching vulnerability data from the Wiz API.

    Returns:
        tuple: A tuple containing the GraphQL query string and the variables dictionary.
    """
    query = """
        query VulnerabilityFindingsPage($filterBy: VulnerabilityFindingFilters, $first: Int, $after: String, $orderBy: VulnerabilityFindingOrder) {
            vulnerabilityFindings(
            filterBy: $filterBy
            first: $first
            after: $after
            orderBy: $orderBy
            ) {
            nodes {
                id
                portalUrl
                name
                CVEDescription
                CVSSSeverity
                score
                exploitabilityScore
                severity
                nvdSeverity
                weightedSeverity
                impactScore
                dataSourceName
                hasExploit
                hasCisaKevExploit
                status
                isHighProfileThreat
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
                artifactType {
                ...SBOMArtifactTypeFragment
                }
                resolutionReason
                epssSeverity
                epssPercentile
                epssProbability
                validatedInRuntime
                layerMetadata {
                id
                details
                isBaseLayer
                }
                projects {
                id
                name
                slug
                businessUnit
                riskProfile {
                    businessImpact
                }
                }
                ignoreRules {
                id
                name
                enabled
                expiredAt
                }
                cvssv2 {
                attackVector
                attackComplexity
                confidentialityImpact
                integrityImpact
                privilegesRequired
                userInteractionRequired
                }
                cvssv3 {
                attackVector
                attackComplexity
                confidentialityImpact
                integrityImpact
                privilegesRequired
                userInteractionRequired
                }
                relatedIssueAnalytics {
                issueCount
                criticalSeverityCount
                highSeverityCount
                mediumSeverityCount
                lowSeverityCount
                informationalSeverityCount
                }
                cnaScore
                vulnerableAsset {
                ... on VulnerableAssetBase {
                    id
                    type
                    name
                    region
                    providerUniqueId
                    cloudProviderURL
                    cloudPlatform
                    nativeType
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
                    imageName
                    computeInstanceGroup {
                    id
                    externalId
                    name
                    replicaCount
                    tags
                    }
                }
                ... on VulnerableAssetServerless {
                    runtime
                }
                ... on VulnerableAssetContainerImage {
                    imageId
                    scanSource
                    registry {
                    name
                    externalId
                    }
                    repository {
                    name
                    externalId
                    }
                    executionControllers {
                    id
                    name
                    entityType
                    externalId
                    providerUniqueId
                    name
                    subscriptionExternalId
                    subscriptionId
                    subscriptionName
                    ancestors {
                        id
                        name
                        entityType
                        externalId
                        providerUniqueId
                    }
                    }
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
            fragment SBOMArtifactTypeFragment on SBOMArtifactType {
        group
        codeLibraryLanguage
        osPackageManager
        hostedTechnology {
            name
        }
        plugin
        custom
        }
    """
    return query

def call_wiz_api(api_url, headers, query, variables):
    #print("Calling Wiz API")
    """
    Executes the GraphQL query to fetch data from the Wiz API.

    Args:
        api_url (str): The URL of the Wiz API.
        headers (dict): The headers for the HTTP request.
        query (str): The GraphQL query string.
        variables (dict): The variables for the GraphQL query.

    Returns:
        dict: The JSON response from the Wiz API, or None on error.
    """
    payload = {
        "query": query,
        "variables": variables
    }
    try:
        #print("Trying WIz API")
        response = requests.post(api_url, headers=headers, json=payload)
        #print(response.json)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Wiz API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}, Response text: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def ol_service_info_query():
    """
    Returns the GraphQL query to retrieve service information from OpsLevel.

    Returns:
        str: The GraphQL query string.
    """
    return """
        query get_service_info_long($alias: String){
        account{
            service(alias: $alias){
            id
            name
            aliases
            codeIssues {
                totalCount
            }
            codeIssueProjects {
                nodes {
                    name
                    externalId
                    id
                }
            }
            }
        }
        }
        """

def ol_codeissue_mutation():
    """
    Returns the GraphQL query to retrieve service information from OpsLevel.
    """
    return """
        mutation codeIssueUpsert($input: CodeIssueInput!) {
            codeIssueUpsert(input: $input) {
            codeIssue {
                id
                name
                externalUrl
                issueType
                severity
                cves {
                identifier
                url
                }
                cwes{
                identifier
                url
                }
            }
            errors {
                message
                path
            }
            }
        }
        """

def ol_codeissueproject_mutation():
    return """
        mutation createCodeIssuProject($identifier: CodeIssueProjectIdentifierInput!, $name: String!, $url: String) {
        codeIssueProjectUpsert(input: {identifier: $identifier, name: $name, url: $url}) {
            codeIssueProject {
            id
            name
            externalUrl
            integration {
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

def ol_x_codeissue_svc_mutation():
    """
    Returns the GraphQL mutation to connect a code issue project to a service in OpsLevel.
    """
    return """
        mutation codeIssueProjectResourceConnect($codeIssueProjectIds: [ID!]!, $resourceId: ID!) {
          codeIssueProjectResourceConnect(input: {
            codeIssueProjectIds: $codeIssueProjectIds,
            resourceId: $resourceId
          }) {
            resource {
              ... on Service {
                id
                name
              }
              ... on Repository {
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

def call_opslevel_api(query: str, variables: str, api_token: str) -> Optional[Dict]:
    """
    Executes a GraphQL query against the OpsLevel API.

    Args:
        query (str): The GraphQL query string.
        variables (dict): A dictionary of variables for the query.
        api_token (str): The OpsLevel API token.

    Returns:
        Optional[Dict]: The JSON response from the API, or None on error.
    """
    endpoint = "https://api.opslevel.com/graphql"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    opslevel_variables = variables

    payload = {"query": query, "variables": opslevel_variables}
    #print((json.dumps(payload, indent=2)))

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        json_response = response.json() # Store the json
        #print(f"OpsLevel API Response: {json_response}")  # Print the response JSON
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        print(f"Failed to connect to OpsLevel API.  Please check your network connection and try again. Error Details: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}. Response text: {response.text}")
        print("The response from the OpsLevel API was not valid JSON.  Please check the API response.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Please check the script and your environment configuration.")
        return None

def check_for_cip(data, name):
    """
    Checks if a dictionary with the name 'Wiz Issues' exists in the given list.

    Args:
        data: A list of dictionaries, where each dictionary is expected to
              have a 'name' key.

    Returns:
        True if a dictionary with 'name' equal to 'Wiz Issues' is found,
        False otherwise.
    """
    #print(data)
    #print(name)
    for item in data:
        #print(name)
        print(item)
        if isinstance(item, dict) and item.get('name') == name:
            status = True
            id = item.get('id')
            return status, id
    return False, None

def sync_vulnerabilities():
    """
    Fetches vulnerability data from the Wiz API and extracts specific fields.

    Returns:
        list: A list of dictionaries, where each dictionary represents a vulnerability
              and contains the extracted fields.  Returns an empty list on error.
    """
    opslevel_token = os.environ.get("OPSLEVEL_API_TOKEN")
    client_id = os.environ.get("WIZ_CLIENT_ID")
    client_secret = os.environ.get("WIZ_CLIENT_SECRET")    
    api_url = "https://api.us17.app.wiz.io/graphql"  # Or your specific Wiz API URL

    api_token = request_wiz_api_token(client_id, client_secret, token_url)  # Get API token from environment variable

    if not api_token:
        print("Error: WIZ_API_TOKEN environment variable not set.")
        return []  # Return an empty list
    if not opslevel_token:
        print("Error: OPSLEVEL_API_TOKEN environment variable not set.")
        return []  # Return an empty list
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_token}",
        "content-type": "application/json",
    }

    query = wiz_vulnerabilities_query() # Get query 
    opslevel_query = ol_service_info_query()
    ol_cip_mutation = ol_codeissueproject_mutation()
    opslevel_mutation = ol_x_codeissue_svc_mutation() # Get the mutation query
    code_issue_mutation = ol_codeissue_mutation()

    #moved here
    variables = {
        "first": 100,  # You can adjust the number of results per page
        "filterBy": {
            "updatedAt": {
            "after": "2025-05-13T13:22:54.500Z"
            },
            "relatedIssueSeverity": "CRITICAL"
        },
        "orderBy": {
        "field": "RELATED_ISSUE_SEVERITY",
        "direction": "DESC"
        }
    }

    all_vulnerabilities = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        variables["after"] = after_cursor
        try: # added try catch
            response_data = call_wiz_api(api_url, headers, query, variables) # Call API
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
                if "Name" in node["vulnerableAsset"]["tags"]:
                    opslevel_dependency_of = node["vulnerableAsset"]["tags"]["Name"]      
                    extracted_data = {
                        "name": node["name"],
                        "external_id": node["id"],
                        "cve_description": node["CVEDescription"],
                        "first_detected_at": node["firstDetectedAt"],
                        "severity": node["severity"],
                        "portal_url": node["portalUrl"],
                        "status": node["status"],
                        "vulnerable_asset_type": node["vulnerableAsset"]["type"],
                        "vulnerable_asset_tags": node["vulnerableAsset"]["tags"],
                        "opslevel_dependency_of": opslevel_dependency_of
                    }
                    # Make OpsLevel API call if opslevel_dependency_of is found
                    opslevel_variables = {
                            "alias": "jtoebes-echo"
                        }
                    if opslevel_dependency_of:
                        opslevel_data = call_opslevel_api(opslevel_query, opslevel_variables, opslevel_token)
                        #print(opslevel_data)
                        if opslevel_data and "data" in opslevel_data and "account" in opslevel_data["data"] and "service" in opslevel_data["data"]["account"]:
                            service_data = opslevel_data["data"]["account"]["service"]
                            extracted_data["opslevel_service_id"] = service_data["id"]
                            extracted_data["opslevel_service_name"] = service_data["name"]
                            extracted_data["opslevel_service_aliases"] = service_data["aliases"]
                            extracted_data["opslevel_code_issues_total_count"] = service_data["codeIssues"]["totalCount"]

                            # Check for Wiz code issues project 
                            # print(service_data["codeIssueProjects"]["nodes"])
                            extracted_data["wiz_code_issues_project_exists"] = any(project["name"] == service_data["codeIssueProjects"]["nodes"] for project in service_data["codeIssueProjects"]["nodes"])
                            #print(extracted_data["wiz_code_issues_project_exists"])
                            #print("Wiz Vulnerabilities: "+ service_data["name"])
                            #  connect the code issue project to the service if wiz_code_issues_project_exists is false
                            print(service_data["codeIssueProjects"]["nodes"])
                            status, cip_id = check_for_cip(service_data["codeIssueProjects"]["nodes"], "Wiz Vulnerabilities: "+ service_data["name"])
                            if not status:
                                print("Project connection does not exist for service")
                                opslevel_cipmutation_variables = {
                                    "identifier": {
                                        "integration": {
                                            "id": integration_id  # Use the provided integration_id
                                        },
                                        "externalId": "Wiz Vulnerabilities: "+ service_data["name"]
                                    },
                                    "url": endpoint_url,
                                    "name": "Wiz Vulnerabilities: "+ service_data["name"]
                                }
                                ol_cipmutation_response = call_opslevel_api(ol_cip_mutation, opslevel_cipmutation_variables, opslevel_token)
                                #print(ol_cipmutation_response)
                                print("Code Issue project id: "+ ol_cipmutation_response["data"]["codeIssueProjectUpsert"]["codeIssueProject"]["id"])
                                opslevel_mutation_variables = {
                                    "resourceId": extracted_data["opslevel_service_id"],  #  service ID
                                    "codeIssueProjectIds": ol_cipmutation_response["data"]["codeIssueProjectUpsert"]["codeIssueProject"]["id"]  # Use the  code issue project ID
                                }
                                opslevel_mutation_response = call_opslevel_api(opslevel_mutation, opslevel_mutation_variables, opslevel_token)
                                #print(opslevel_mutation_response)
                                if opslevel_mutation_response:
                                    extracted_data["opslevel_code_issue_project_connection"] = opslevel_mutation_response["data"]["codeIssueProjectResourceConnect"]["resource"]["id"]
                                else:
                                    extracted_data["opslevel_code_issue_project_connection_error"] = "Failed to connect code issue project"
                            else:
                                #extracted_data["opslevel_code_issue_project_connection"] = "Exists"
                                extracted_data["opslevel_code_issue_project_connection"] = cip_id
                                # print("Project connection exists")
                        else:
                            extracted_data["opslevel_error"] = "Service not found or error fetching data"
                        code_issue_variable = {
                                            "input": {
                                                "identifier": {
                                                    "codeIssueProject": {
                                                        "integration": {
                                                            "id": integration_id  # This ID is a placeholder
                                                        },
                                                        "externalId": "Wiz Vulnerabilities: "+ service_data["name"]
                                                    },
                                                    "externalId": extracted_data["external_id"] 
                                                },
                                                "name": extracted_data["name"],
                                                "issueCategory": "Infrastructure",  # Hardcoded
                                                "severity": extracted_data["severity"],
                                                "cves": {
                                                    "identifier": ((extracted_data["cve_description"][:58] + '..') if len(extracted_data["cve_description"]) > 75 else extracted_data["cve_description"]),
                                                    "url": extracted_data["portal_url"],
                                                }
                                            }
                                        }
                        print(code_issue_mutation)
                        print(code_issue_variable)
                        code_issue_response = call_opslevel_api(code_issue_mutation, code_issue_variable, opslevel_token)
                        print(extracted_data["opslevel_code_issue_project_connection"])
                        print(code_issue_response)
                    all_vulnerabilities.append(extracted_data)

            has_next_page = page_info["hasNextPage"]
            after_cursor = page_info["endCursor"]
        else:
            print("Error: \'data\' or \'vulnerabilityFindings\' not found in response.")
            return []
    #print(all_vulnerabilities)
    #print(len(all_vulnerabilities))
    return all_vulnerabilities
    
if __name__ == "__main__":
    vulnerabilities = sync_vulnerabilities()
    if vulnerabilities:
        print(json.dumps(vulnerabilities, indent=2))  # Pretty print the output
        print(len(vulnerabilities))
    else:
        print("No vulnerabilities found or error occurred.")