import requests
import json
import os  # Import the os module

def update_property(api_url, opslevel_token, alias, definition_alias, value):
    """
    Calls the update_property mutation.

    Args:
        api_url: The URL of the GraphQL API.
        alias: The alias of the owner.
        definition_alias: The alias of the property definition.
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
        "alias": alias,
        "definition_alias": definition_alias,
        "value": json.dumps(value)  # Important: Convert value to JSON string
    }

    headers = {
        "Authorization": f"Bearer {opslevel_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": mutation,
        "variables": json.dumps(variables)
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling update_property mutation: {e}")
        return None
    except json.JSONDecodeError as e:
      print(f"Error decoding JSON response: {e}. Response text: {response.text}")
      return None

def get_cloudzero_billing_costs(start_date, end_date, granularity="daily", cost_type="real_cost"):
    """
    Calls the CloudZero Billing Costs API to retrieve cost data.

    Args:
        start_date (str): The start date for the cost data in ISO 8601 format (e.g., "2025-01-01T00:00:00Z").
        end_date (str): The end date for the cost data in ISO 8601 format (e.g., "2025-01-31T23:59:59Z").
        granularity (str, optional): The granularity of the cost data (e.g., "daily", "monthly"). Defaults to "daily".
        cost_type (str, optional): The type of cost to retrieve (e.g., "real_cost", "amortized_cost"). Defaults to "real_cost".

    Returns:
        dict: The JSON response from the API if the request is successful, None otherwise.
    """
    api_key = os.environ.get("CLOUDZERO_API_KEY")
    if not api_key:
        print("Error: CLOUDZERO_API_KEY environment variable not set.")
        return None

    url = "https://api.cloudzero.com/v2/billing/costs"
    headers = {
        "accept": "application/json",
        "Authorization": api_key  # Assuming API key is passed as a header
    }
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "cost_type": cost_type,
        "group_by": ["Tag:Name"]
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling CloudZero API: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            try:
                print(f"Response body: {response.json()}")
            except:
                print(f"Response body: {response.text}")
        return None

if __name__ == "__main__":
    api_url = 'https://api.opslevel.com/graphql'  # Replace with your actual API URL
    opslevel_token = os.environ.get("OPSLEVEL_API_TOKEN")
    definition_alias = "aws_cost"
    start_date = "2025-05-01T00:00:00Z"
    end_date = "2025-05-09T00:00:00Z"  # Adjust the end date as needed
    if not opslevel_token:
        print("Error: OPSLEVEL_API_TOKEN environment variable not set.")

    billing_data = get_cloudzero_billing_costs(start_date, end_date)

    if billing_data:
        print("CloudZero Billing Costs:")
        # Group data by tag and sum costs, ignoring "__NULL_PARTITION_VALUE__"
        grouped_data = {}
        for item in billing_data['costs']:
            tag_name = item["Tag:Name"]
            cost = item["cost"]
            if tag_name != "__NULL_PARTITION_VALUE__":  # Ignore this tag name
                if tag_name in grouped_data:
                    grouped_data[tag_name]["cost"] += cost
                    grouped_data[tag_name]["usage_dates"].append(item["usage_date"])
                else:
                    grouped_data[tag_name] = {"cost": cost, "usage_dates": [item["usage_date"]]}

        # Convert the grouped data to the desired JSON format
        result = [{"Tag_Name": tag, "Cost": data["cost"], "Usage_Dates": data["usage_dates"]} for tag, data in grouped_data.items()]
        for item in result:
            print(item)
            ol_prop_update_result = update_property(api_url, opslevel_token, item["Tag_Name"], definition_alias, item["Cost"])
            if ol_prop_update_result:
                print("Update Result:", json.dumps(ol_prop_update_result, indent=2))
                #print("Update Result:")
            else:
                print("Property update failed.")
        # Print the JSON output
        print(json.dumps(result, indent=2))
    else:
        print("Failed to retrieve CloudZero billing costs.")