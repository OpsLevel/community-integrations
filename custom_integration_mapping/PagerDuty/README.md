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

1.  **Define Custom Properties**: On the Component Edit Page, define a relevant custom property:
    *   **PD Service ID**: Type `Text` (String).

    <img width="1772" height="1282" alt="image" src="https://github.com/user-attachments/assets/32e61f2f-6779-4a05-9bbd-f3ae6544c402" />


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
      iterator: ".services"
      http_polling:
        method: GET
        url: https://api.pagerduty.com/services?limit=500
        headers:
        - name: Authorization
          value: Token token={{ 'pd_token' | secret }}
        - name: Accept
          value: application/vnd.pagerduty+json;version=2
    ```
*   **`external_kind`**: A unique identifier for the type of data being extracted.
*   **`external_id: ".id"`**: A JQ expression to select PagerDuty's Service ID as the unique identifier.
*   **`iterator: ".services"`**: This JQ expression tells OpsLevel to iterate over each service in PagerDuty's response, treating each as an individual object.
*   **`http_polling`**: This section defines how OpsLevel will actively poll the PagerDuty API.
*   **`method: GET`**: The HTTP method for the API call.
*   **`limit=500`**: This config does not implement pagination handling. Setting `limit=500` (PagerDuty's documented maximum) avoids silent truncation.

### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted PagerDuty data to your OpsLevel component properties.

1. **Define Transformer**: Configure the transform definition in YAML as follows:

    ```yaml
    ---
    transforms:
    - external_kind: pagerduty_service
      opslevel_kind: service
      opslevel_identifier: .name | ascii_downcase | gsub(" "; "-")
      on_component_not_found: suggest
      properties:
        pd_service_id: ".id"
    ```
*   **`external_kind: pagerduty_service`**: This maps the extracted PagerDuty data to the custom properties in OpsLevel.
*   **`opslevel_kind: service`**: This maps PagerDuty services to the correct component type in OpsLevel (service).
*   **`opslevel_identifier`**: This expression matches PagerDuty service names to OpsLevel service aliases by lowercasing the name and converting spaces to dashes.
*   **`on_component_not_found: suggest`**: Defaults to surfacing any unmatched PagerDuty services as detected component recommendations (Catalog > Detected Components) rather than silently discarding them — this gives you visibility into what didn't match, rather than assuming the alias logic worked correctly.
    * **Consider `skip` instead if your PagerDuty setup doesn't map 1:1 to OpsLevel Services** — for example, if your organization has set up PagerDuty Services per-team rather than per-service. In that case, most PagerDuty "services" won't correspond to any single OpsLevel service alias, and `suggest` would generate a large number of irrelevant detected-component recommendations. Use `skip` to suppress those instead:
    ```yaml
        on_component_not_found: skip
    ```

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
Note: `.service.properties.pd_service_id` resolves via the property's **identifier**, not its display name — confirm this matches the identifier shown on your property's Edit page (Step 1) if you named it something other than `pd_service_id`, since identifiers are auto-generated from the display name and may not match exactly (e.g. spaces, casing).

This is especially useful for Actions that trigger PagerDuty incidents directly from OpsLevel, where the Service ID needs to be passed in the payload.

---

### Important Considerations

*   **Pagination**: This template does not paginate beyond `limit=500`. If you have more services than that in PagerDuty, some will not be synced. Verify your total service count in PagerDuty before relying on this integration for full coverage.
*   **Alias matching**: The `opslevel_identifier` JQ expression above is a best-effort default, not a universal solution. Test it against a small number of services first (see Step 6) before trusting it across your full catalog.
*   **JQ expressions**: Both the extractor and transform definitions use [JQ](https://jqlang.org/) syntax to parse and reshape API responses. If you're unfamiliar with JQ, [jqplay.org](https://jqplay.org) is a useful sandbox for testing expressions against sample PagerDuty payloads before wiring them into the live integration.

---
