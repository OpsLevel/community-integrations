# FireHydrant custom integration setup: Pull the service catalog from FireHydranr into your OpsLevel catalog

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel to import services from FireHydrant.

## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:
*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as will be demonstrated with FireHydrant.

The process involves a two-stage approach:
1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.


## Setup Instructions

### Step 1: Customize the Service property schema


1.  **Define Custom Properties**: On the Component Edit Page, define relevant custom properties:
    *   **Name**: Type `Text` (String).
    *   **Incident Count**: Type `Number` (Number).
    <img width="1772" height="1282" alt="image" src="https://github.com/user-attachments/assets/109c11a0-136b-4485-b554-0d8d14c55438" />




### Step 2: Create a Secret in OpsLevel for FireHydrant Authentication

You'll need a secret to store your FireHydrant API token for authentication.

1.  **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2.  **Create New Secret**:
    *   **Name**: `firehydrant_api_key`.


### Step 3: Create a Custom Integration Mapping in OpsLevel

This step initiates the custom integration process.

1.  **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2.  **Add Custom Integration**: Select the **Custom** integration option.
3.  **Name the Integration**: You can name it `FireHydrant Catalog Sync`.

### Step 4: Configure the Extract Definition

The extract definition specifies how OpsLevel will pull data from FireHydrant.

1.  **Access Configuration**: Within your custom FireHydrant integration, find the **Extract and Transform Configuration** section.
2.  **Define Extractor**: Configure the extractor definition in YAML as follows:

    ```yaml
    ---
    extractors:
    - external_kind: firehydrant
      iterator: ".[]"
      external_id: ".id"
      http_polling:
        method: GET
        url: https://api.firehydrant.io/v1/services
        headers:
      - name: Accept
        value: application/json
      - name: Authorization
        value: Bearer {{ 'firehydrant_api_key' | secret }}
    ```
    *   **`external_kind`**: A unique identifier for the type of data being extracted.
    *   **`iterator: "."`**: This JQ expression tells OpsLevel to iterate over each item in the FireHydrant API response, treating each as an individual object.
    *   **`external_id: ".id"`**: A JQ expression to select a value that uniquely identifies the service in FireHydrant (e.g., the service ID).
    *   **`http_polling`**: This section defines how OpsLevel will actively poll the FireHydrant API.
        *   **`method: GET`**: The HTTP method for the API call.


### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted FireHydrant data to your OpsLevel component properties and relationships.

1.  **Define Transformer**: Configure the transform definition in YAML as follows:

    ```yaml
    ---
    transforms:
    - external_kind: firehydrant
      on_component_not_found: suggest
      opslevel_kind: service
      opslevel_identifier: ".slug"
      properties:
       name: ".name"
       incident_count: ".active_incidents | length"
    ```
    *   **`external_kind: firehydrant`**: This is mapping the data of the firehydrant extractor to the custom properties in OpsLevel.
    *   **`opslevel_kind: service`**: This is mapping the data of the FireHydrant services to the correct component type in OpsLevel (service).
    *   **`on_component_not_found: suggest`**: Specifies the custom integration to suggest any FireHydrant slugs that do not match an OpsLevel service alias to the detected component recommendations.


### Step 6: Test and Sync the Integration

After configuring both definitions, you can test and activate your integration.

1.  **Run Test**: Use the "Run Test" feature within the custom integration interface. This will execute the API call to FireHydrant, return the actual payload, and allow you to inspect the data, verifying how it maps to properties and which new components will be suggested.
2.  **Save Configuration**: Save your Extraction and Transform Definitions.
3.  **Observe Components**: Once the sync completes, you will see your service data data mapped to services in your OpsLevel catalog.
    *   **Managed Properties**: Properties managed by the integration (e.g., Incident COunt, etc) will be **locked** and cannot be updated directly from the OpsLevel UI or API; updates must come via the integration itself.

### Step 7: After the integration syncs check out new detected component recommendations

1.  **Navigate to Detected Components**: In OpsLevel, go to **Catalog > Detected Components**.
2.  **Filter FireHydrant Integration**: View the suggestions from the new FireHydrant custom integration

   <img width="2298" height="896" alt="image" src="https://github.com/user-attachments/assets/3d124120-83ef-483f-ac24-eaa42c193df5" />


  
