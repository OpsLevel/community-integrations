# PagerDuty custom integration setup: Pull the service catalog from PagerDuty into your OpsLevel catalog

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel to import PagerDuty Service IDs into your OpsLevel catalog, enabling Custom Actions (e.g. triggering PagerDuty incidents) without manually tagging each service.

## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:
*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as will be demonstrated with PagerDuty.

The process involves a two-stage approach:
1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.


## Setup Instructions

### Step 1: Customize the Service property schema

**Define Custom Properties**: On the Component Edit Page, define a relevant custom property:
    *   **PD Service ID**: Type `Text` (String).
      <img width="1321" height="948" alt="image" src="https://github.com/user-attachments/assets/32e61f2f-6779-4a05-9bbd-f3ae6544c402" />


### Step 2: Create a Secret in OpsLevel for PagerDuty Authentication

You'll need a secret to store your PagerDuty API token for authentication.

1.  **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2.  **Create New Secret**:
    *   **Name**: `pd_token`.

### Step 3: Create a Custom Integration Mapping in OpsLevel

This step initiates the custom integration process.

1.  **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2.  **Add Custom Integration**: Select the **Custom** integration option.
3.  **Name the Integration**: You can name it `PagerDuty Service Sync`.

### Step 4: Configure the Extract Definition

The extract definition specifies how OpsLevel will pull data from PagerDuty.

1.  **Access Configuration**: Within your custom PagerDuty integration, find the **Extract and Transform Configuration** section.
2.  **Define Extractor**: Configure the extractor definition in YAML as follows:

```yaml
---
extractors:
- external_kind: pagerduty_service
  external_id: ".id"
  http_polling:
    url: https://api.pagerduty.com/services?limit=100
    method: GET
    headers:
    - name: Authorization
      value: Token token={{ 'pd_token' | secret }}
    - name: Accept
      value: application/vnd.pagerduty+json;version=2
  iterator: ".services"
```
*   **`external_kind`**: A unique identifier for the type of data being extracted.
*   **`external_id: ".id"`**: A JQ expression to select PagerDuty's Service ID as the unique identifier.
*   **`http_polling`**: This section defines how OpsLevel will actively poll the PagerDuty API.
*   **`method: GET`**: The HTTP method for the API call.
*   **`iterator: ".services"`**: This JQ expression tells OpsLevel to iterate over each service in PagerDuty's response, treating each as an individual object.

### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted PagerDuty data to your OpsLevel component properties.

**Define Transformer**: Configure the transform definition in YAML as follows:

```yaml
---
transforms:
- external_kind: pagerduty_service
  opslevel_kind: service
  opslevel_identifier: .name | ascii_downcase | gsub(" "; "-")
  on_component_not_found: skip
  properties:
    pd_service_id: ".id"

```
*   **`external_kind: pagerduty_service`**: This maps the extracted PagerDuty data to the custom properties in OpsLevel.
*   **`opslevel_kind: service`**: This maps PagerDuty services to the correct component type in OpsLevel (service).
*   **`opslevel_identifier`**: Matches PagerDuty service names to OpsLevel service aliases (lowercased, spaces converted to dashes). If your PagerDuty service names don't align with your OpsLevel aliases, adjust this expression accordingly.
*   **`on_component_not_found: skip`**: Silently skips any PagerDuty services that don't match an existing OpsLevel service alias, rather than creating new components or suggestions. Use `suggest` instead if you'd rather review unmatched services as detected component recommendations.

### Step 6: Test and Sync the Integration

After configuring both definitions, you can test and activate your integration.

1.  **Run Test**: Use the "Run Test" feature within the custom integration interface. This will execute the API call to PagerDuty, return the actual payload, and allow you to inspect the data, verifying how it maps to properties.
2.  **Save Configuration**: Save your Extraction and Transform Definitions.
3.  **Observe Components**: Once the sync completes, your services will have the `PD Service ID` property populated automatically.
    *   **Managed Properties**: Properties managed by the integration (e.g. `PD Service ID`) will be **locked** and cannot be updated directly from the OpsLevel UI or API; updates must come via the integration itself.

### Step 7: Reference the property in a Custom Action

Once `PD Service ID` is populated, you can reference it in a Custom Action's manual input using `defaultValueExpression`, avoiding the need to manually tag each service:

```yaml
version: 1
inputs:
  - identifier: pd_service_id
    displayName: PagerDuty Service ID
    type: text_input
    defaultValueExpression: .service.properties.pd_service_id
    required: true
```

This is especially useful for Actions that trigger PagerDuty incidents directly from OpsLevel, where the Service ID needs to be passed in the payload.
