# OpsLevel Custom Integration with Rootly: Pull incidents from Rootly into your software catalog

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel to track Rootly incidents as components in your software catalog.

## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:
*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as will be demonstrated with Jira.

The process involves a two-stage approach:
1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.

## Setup Instructions

### Step 1: Create a Custom Component Type for Rootly Incidents in OpsLevel

You'll need to define a new component type in OpsLevel to represent your Rootly incidents.

1.  **Navigate to Component Types**: In OpsLevel, go to **Settings > Component Types**.
2.  **Create New Component Type**: Select **+ New Component Type**. [Documentation](https://docs.opslevel.com/docs/components)
3.  **Define "Incident" Component Type**:
    *   **Display Name**: Enter `Incident`.
    *   **Identifier**: The identifier will be auto-generated; you can keep it or change it.
    *   **Description**: Provide helper text (e.g., "Used to track Rootly incidents related to services").
    *   **Customize Icon** (Optional): You can customize the icon for this component type.
    *   Press **Save**.
    <img width="2304" height="1060" alt="image" src="https://github.com/user-attachments/assets/82578b19-6a23-4b83-9dbb-0047e123c7d5" />

4.  **Define Custom Properties**: On the Component Edit Page, define the following custom properties:
    *   **Service ID**: Type `Array` (String).
    *   **Severity**: Type `Text` (String).
    *   **Status**: Type `Text` (String).
    *   **Summary**: Type `Text` (String).
    *   **Rootly Service ID**: Type `Text` (String). This property will be added to "Service" component type in OpsLevel and will be used in the relationship that will be set up in step 1.5.
    *   **Display Status**: For `Service IDs`, consider hiding them if they are primarily used for mapping relationships and not necessary for direct display to component owners.
    <img width="2008" height="1252" alt="image" src="https://github.com/user-attachments/assets/dcab2b10-23e3-4d9b-925b-102c351fc396" />


5.  **Define Custom Relationships**: Establish relationships to link Jira tickets to existing services and teams in OpsLevel:
    *   **Associated Service**:
        *   **Display Name**: `Service Incidents`.
        *   **Identifier**: `associated_service`.
        *   **Allowed Types**: Select `Service`.
        *   **Management Rule**: Set a rule to automatically associate the Rootly incidents to a service based on the `Service IDs` array.
<img width="1527" height="1075" alt="image" src="https://github.com/user-attachments/assets/c766e25d-7950-4d84-8631-90e054dd3f36" />

### Step 2: Create a Secret in OpsLevel for Rootly Authentication

You'll need a secret to store your Jira API token for authentication.

1.  **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2.  **Create New Secret**:
    *   **Name**: `rootly_token`.


### Step 3: Create a Custom Integration Mapping in OpsLevel

This step initiates the custom integration process.

1.  **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2.  **Add Custom Integration**: Select the **Custom** integration option.
3.  **Name the Integration**: You can name it `Rootly (Incidents)`.

### Step 4: Configure the Extraction Definition

The extraction definition specifies how OpsLevel will pull data from Jira.

1.  **Access Configuration**: Within your custom Rootly integration, find the **Extract and Transform Configuration** section.
2.  **Define Extractor**: Configure the extractor definition in YAML as follows:

    ```yaml
    ---
    extractors:
      - external_kind: rootly_incidents
        external_id: ".id"
        iterator: ".[]"
        http_polling:
          method: GET
          url: https://api.rootly.com/v1/incidents
          headers:
          - name: Content-Type
            value: application/json
          - name: Authorization
            value: Bearer {{ 'rootly_token' | secret }}
     - external_kind: rootly_services
       external_id: ".attributes.slug"
       iterator: ".included"
       http_polling:
         method: GET
         url: https://api.rootly.com/v1/incidents?include=services
         headers:
         - name: Content-Type
           value: application/json
         - name: Authorization
           value: Bearer {{ 'rootly_token' | secret }}
           
    ```
    *   **`external_kind: rootly_incidents`**: A unique identifier for the type of data being extracted.
    *   **`iterator: ".[]"`**: This JQ expression tells OpsLevel to iterate over each item in the Rootly API response, treating each as an individual object.
    *   **`external_id: ".id"`**: A JQ expression to select a value that uniquely identifies the incidents in Rootly (e.g., the Incident ID).
    *   **`http_polling`**: This section defines how OpsLevel will actively poll the Rootly API.
        *   **`method: GET`**: The HTTP method for the API call.


### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted Rootly data to your OpsLevel component properties and relationships.

1.  **Define Transformer**: Configure the transform definition in YAML as follows:

    ```yaml
    ---
    transforms:
      - external_kind: rootly_incidents
        on_component_not_found: create
        opslevel_kind: incident
        opslevel_identifier: ".attributes.slug"
        properties:
          name: ".attributes.title"
          status: ".attributes.status"
          severity: ".attributes.severity.data.attributes.name"
          summary: ".attributes.summary"
          url: ".attributes.url"
          service_id: ".relationships.services.data | map(.id)"
     - external_kind: rootly_services
       on_component_not_found: suggest
       opslevel_kind: service
       opslevel_identifier: ".attributes.slug"
       properties:
         rootly_service_id: ".id"

    ```
    *   **`external_kind: rootly_incidents`**: This is mapping the data of the Rootly incidents to the custom properties in OpsLevel.
    *   **`external_kind: rootly_services`**: This is suggesting Rootly services in OpsLevel detected component recommendations if they do not already exist in the OpsLevel catalog.
    *   **`on_component_not_found: create`**: Specifies that if an OpsLevel component matching the `opslevel_identifier` is not found, a new incidents should be created or service suggested. Other options include `skip`.


### Step 6: Test and Sync the Integration

After configuring both definitions, you can test and activate your integration.

1.  **Run Test**: Use the "Run Test" feature within the custom integration interface. This will execute the API call to Rootly, return the actual payload, and allow you to inspect the data, verifying how it maps to properties and which new components will be created.
2.  **Save Configuration**: Save your Extraction and Transform Definitions.
3.  **Observe Components**: Once the sync completes, you will see your Rootly incidents appear as new `Incident` components in your OpsLevel catalog.
    *   **Managed Properties**: Properties managed by the integration (e.g., Status, Severity) will be **locked** and cannot be updated directly from the OpsLevel UI or API; updates must come via the integration itself.
    *   **Relationships**: The relationships you defined (Associated Service/Service Incidents) will be automatically established. [Documentation](https://docs.opslevel.com/docs/mapping-integration-data-to-custom-properties)

---

## Important Considerations

*   **JQ Expressions**: The system relies on JQ expressions for data extraction and transformation. Leverage [JQ](https://jqlang.org/manual/v1.6/) for transformations.
*   **Filtering Data**: For large datasets like Jira tickets, utilize the `exclude` parameter in the extraction definition to filter out unwanted data, preventing the catalog from becoming overloaded. Leverage the Jira API parameters for filtering.
