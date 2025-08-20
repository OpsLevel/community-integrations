# CloudZero to OpsLevel Cost Integration

This repository contains a sample Python script to integrate cost data from CloudZero into your OpsLevel service catalog. By leveraging the CloudZero and OpsLevel APIs, this integration provides visibility into infrastructure cloud costs associated with services in your catalog.

## How it Works

The integration follows these steps:
1.  **Fetch Cost Data:** The script calls the CloudZero Billing Costs API (`/v2/billing/costs`) to retrieve cost data for a specified date range.
2.  **Group by Tag:** It groups the cost data using a specific tag, such as "Tag:Name", which helps associate infrastructure resources with services in your catalog. The example script specifically ignores costs associated with "__NULL_PARTITION_VALUE__".
3.  **Aggregate Costs:** For each unique tag name, the script aggregates the total cost.
4.  **Update OpsLevel Properties:** It then calls the OpsLevel GraphQL API using the `propertyAssign` mutation to update a custom property on the corresponding service in your OpsLevel catalog. The tag name from CloudZero is used as the service alias (owner alias) in OpsLevel, and the aggregated cost is assigned as the property value.

## Prerequisites

To use this integration, you need:
*   **A CloudZero Account:** With an API key enabled.
*   **Integrated Cloud Infrastructure:** Your cloud infrastructure (e.g., AWS) should be integrated with CloudZero.
*   **Cost Allocation Tags:** **Cost allocation tags must be enabled and used on your cloud resources**. The integration leverages these tags, particularly the "Name" tag in the example, to relate infrastructure costs to services in OpsLevel.
*   **An OpsLevel Account:** With an API token.
*   **OpsLevel Custom Property:** A custom property definition must be created in OpsLevel to hold the cost data, for example, a JSON property named "aws_cost".
*   **Python Environment:** A Python environment with the `requests` library installed.

## Setup

1.  **Configure Environment Variables:**
    *   Set the `CLOUDZERO_API_KEY` environment variable with your CloudZero API key.
    *   Set the `OPSLEVEL_API_TOKEN` environment variable with your OpsLevel API token.
    *   If these variables are not set, the script will print an error and exit.

2.  **Define OpsLevel Custom Property:**
    *   Ensure you have a custom property defined in OpsLevel. The example script uses the alias `"aws_cost"`. This property will store the cost value for each service. The property value is stored as a JSON string in OpsLevel.

3.  **Configure Script Parameters:**
    *   Adjust the config dictionary within the main() function to match your requirements:

    ```
    config = {
        'opslevel_api_url': 'https://api.opslevel.com/graphql',  # Your OpsLevel GraphQL API URL
        'opslevel_token_env_var': "OPSLEVEL_API_TOKEN", # Environment variable for OpsLevel API token
        'opslevel_definition_alias': "aws_cost", # Alias of the OpsLevel property definition (e.g., "aws_cost")
        'cloudzero_api_key_env_var': "CLOUDZERO_API_KEY", # Environment variable for CloudZero API key
        'cloudzero_start_date': "2025-05-01T00:00:00Z", # Start date for CloudZero costs (ISO 8601 format)
        'cloudzero_end_date': "2025-05-09T00:00:00Z",  # End date for CloudZero costs (ISO 8601 format)
        'cloudzero_granularity': "daily", # Granularity for CloudZero costs ("daily", "monthly")
        'cloudzero_cost_type': "real_cost" # Cost type for CloudZero costs ("real_cost", "amortized_cost")
    }
    ```

## Script Usage

1.  **Install Dependencies:**
    ```bash
    pip install requests
    ```
2.  **Run the Script:**
    ```bash
    python get_cloudzero_billing_costs.py
    ```

The script will fetch data from CloudZero, process it, and attempt to update the specified custom property on services in OpsLevel whose aliases match the "Tag:Name" value from CloudZero.

The script includes error handling for API calls and JSON decoding. It will print status updates and results.

## Visualizing Costs in OpsLevel

Once the script has populated the custom property, you can view the cost information within OpsLevel:

*   **Service Details Page:** The cost will appear as a custom property on the individual service's page.
*   **Team Dashboard Widget:** You can add a custom widget to a team's dashboard to display a breakdown of costs for services owned by that team. This widget uses a GraphQL query to fetch the custom property value for all services within the team. The example shows this as a pie chart widget providing a cost breakdown by service.

## Extensibility

While this example specifically integrates with CloudZero and uses "Tag:Name" for grouping, the approach of fetching cost data and pushing it to OpsLevel custom properties can be extended. You could use other data sources like the AWS Cost Explorer APIs or APIs from different infrastructure cost management tools.