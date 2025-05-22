import requests
import json
import os  # Import the os module

def update_property(opslevel_api_url, opslevel_api_token, owner_alias, prop_definition_alias, value):
    """
    Calls the update_property mutation.

    Args:
        opslevel_api_url: The URL of the GraphQL API for OpsLevel.
        opslevel_api_token: The API token for OpsLevel.
        owner_alias: The alias of the owner.
        prop_definition_alias: The alias of the property definition.
        value: The new value for the property.

    Returns:
        The JSON response from the mutation, or None if an error occurs.
    """

    mutation = """
    mutation update_property($alias:String, $definition_alias:String, $value:JsonString!){
      propertyAssign(input: {owner: {alias: $alias}, definition: {alias: $definition_alias},
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

    variables = {
        "alias": owner_alias,
        "definition_alias": prop_definition_alias,
        "value": json.dumps(value)  # Important: Convert value to JSON string
    }

    headers = {
        "Authorization": f"Bearer {opslevel_api_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": mutation,
        "variables": json.dumps(variables)
    }

    try:
        response = requests.post(opslevel_api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling update_property mutation: {e}")
        return None
    except json.JSONDecodeError as e:
      print(f"Error decoding JSON response: {e}. Response text: {response.text}")
      return None

def get_cloudzero_billing_costs(cz_api_key, cz_api_url, cz_start_date, cz_end_date, granularity="daily", cost_type="real_cost"):
    """
    Calls the CloudZero Billing Costs API to retrieve cost data.

    Args:
        cz_api_key (str): The CloudZero API key.
        cz_api_url (str): The URL for the CloudZero billing costs API.
        cz_start_date (str): The start date for the cost data in ISO 8601 format (e.g., "2025-01-01T00:00:00Z").
        cz_end_date (str): The end date for the cost data in ISO 8601 format (e.g., "2025-01-31T23:59:59Z").
        granularity (str, optional): The granularity of the cost data (e.g., "daily", "monthly"). Defaults to "daily".
        cost_type (str, optional): The type of cost to retrieve (e.g., "real_cost", "amortized_cost"). Defaults to "real_cost".

    Returns:
        dict: The JSON response from the API if the request is successful, None otherwise.
    """
    if not cz_api_key:
        print("Error: CloudZero API key not provided to function.")
        return None

    headers = {
        "accept": "application/json",
        "Authorization": cz_api_key
    }
    params = {
        "start_date": cz_start_date,
        "end_date": cz_end_date,
        "granularity": granularity,
        "cost_type": cost_type,
        "group_by": ["Tag:Name"]
    }

    try:
        response = requests.get(cz_api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling CloudZero API: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            try:
                print(f"Response body: {response.json()}")
            except json.JSONDecodeError:
                print(f"Response body: {response.text}")
        return None

if __name__ == "__main__":
    # --- Configuration Variables ---
    # API Keys from environment variables
    CLOUDZERO_API_KEY = os.environ.get("CLOUDZERO_API_KEY")
    OPSLEVEL_API_TOKEN = os.environ.get("OPSLEVEL_API_TOKEN")

    # OpsLevel API URL (as requested: api_url)
    api_url = 'https://api.opslevel.com/graphql'

    # OpsLevel Property Definition Alias (as requested: definition_alias, value: "aws_cost")
    definition_alias = "aws_cost"

    # Date Range for CloudZero (as requested: start_date, end_date)
    start_date = "2025-05-01T00:00:00Z"
    end_date = "2025-05-09T00:00:00Z"  # Adjust the end date as needed

    # CloudZero API URL (separated for clarity and configurability)
    cloudzero_costs_api_url = "https://api.cloudzero.com/v2/billing/costs"
    # --- End of Configuration Variables ---

    # Validate that API keys are set
    if not CLOUDZERO_API_KEY:
        print("Error: CLOUDZERO_API_KEY environment variable not set.")
    if not OPSLEVEL_API_TOKEN:
        print("Error: OPSLEVEL_API_TOKEN environment variable not set.")

    # Proceed only if both API keys are available
    if CLOUDZERO_API_KEY and OPSLEVEL_API_TOKEN:
        billing_data = get_cloudzero_billing_costs(
            cz_api_key=CLOUDZERO_API_KEY,
            cz_api_url=cloudzero_costs_api_url,
            cz_start_date=start_date,
            cz_end_date=end_date
        )

        if billing_data:
            print("CloudZero Billing Costs Retrieved.")
            # Group data by tag and sum costs, ignoring "__NULL_PARTITION_VALUE__"
            grouped_data = {}
            for item in billing_data.get('costs', []): # Use .get for safety
                tag_name = item.get("Tag:Name")
                cost = item.get("cost")
                if tag_name and cost is not None and tag_name != "__NULL_PARTITION_VALUE__":  # Ignore this tag name and ensure values exist
                    if tag_name in grouped_data:
                        grouped_data[tag_name]["cost"] += cost
                        grouped_data[tag_name]["usage_dates"].append(item.get("usage_date"))
                    else:
                        grouped_data[tag_name] = {"cost": cost, "usage_dates": [item.get("usage_date")]}

            # Convert the grouped data to the desired JSON format
            result = [{"Tag_Name": tag, "Cost": data["cost"], "Usage_Dates": data["usage_dates"]} for tag, data in grouped_data.items()]

            print("\nProcessing and Updating OpsLevel Properties:")
            for item in result:
                print(f"  Updating property for Tag: {item['Tag_Name']}, Cost: {item['Cost']}")
                ol_prop_update_result = update_property(
                    opslevel_api_url=api_url,                   # OpsLevel API URL
                    opslevel_api_token=OPSLEVEL_API_TOKEN,      # OpsLevel Token
                    owner_alias=item["Tag_Name"],               # Owner alias (using Tag_Name)
                    prop_definition_alias=definition_alias,     # Property definition alias ("aws_cost")
                    value=item["Cost"]                          # Value to set (the cost)
                )
                if ol_prop_update_result:
                    if ol_prop_update_result.get("errors"):
                        print(f"    Error updating OpsLevel: {json.dumps(ol_prop_update_result['errors'], indent=2)}")
                    else:
                        print(f"    Update Result: {json.dumps(ol_prop_update_result, indent=2)}")
                else:
                    print("    Property update failed (no response or error in request).")

            # Print the final JSON output of processed data
            print("\nFinal Processed CloudZero Data:")
            print(json.dumps(result, indent=2))
        else:
            print("Failed to retrieve CloudZero billing costs.")
    else:
        print("Cannot proceed: One or both API keys (CLOUDZERO_API_KEY, OPSLEVEL_API_TOKEN) are missing.")