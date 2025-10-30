# Honeycomb IO custom integration setup: Pull SLOs from Honeycomb into your software catalog

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel to track SLOs from Honeycomb and map SLO data to components in your software catalog.

*Note: the following example is related to a latency SLO, but can be customized for visualizing any SLO data.*
<br/>
## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:
*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as will be demonstrated with Honeycomb.

The process involves a two-stage approach:
1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.


## Setup Instructions

### Step 1: Customize the Service property schema


1.  **Define Custom Properties**: On the Component Edit Page, define the following custom properties:
    *   **Latency Target**: Type `Text` (String).
    *   **Budget Remaining**: Type `Text` (String).
    *   **Compliance**: Type `Text` (String).
    <img width="1086" height="817" alt="image" src="https://github.com/user-attachments/assets/d4276556-335e-4b94-90aa-551d5bb4f76b" />



### Step 2: Create a Secret in OpsLevel for Honeycomb Authentication

You'll need a secret to store your Honeycomb API token for authentication.

1.  **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2.  **Create New Secret**:
    *   **Name**: `honeycomb_api_key`.


### Step 3: Create a Custom Integration Mapping in OpsLevel

This step initiates the custom integration process.

1.  **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2.  **Add Custom Integration**: Select the **Custom** integration option.
3.  **Name the Integration**: You can name it `Honeycomb IO SLOs`.

### Step 4: Configure the Extract Definition

The extract definition specifies how OpsLevel will pull data from Honeycomb.

1.  **Access Configuration**: Within your custom Honeycomb integration, find the **Extract and Transform Configuration** section.
2.  **Define Extractor**: Configure the extractor definition in YAML as follows:

    ```yaml
    ---
    extractors:
    - external_kind: honeycomb_slos
      iterator: "."
      external_id: ".id"
      http_polling:
        method: GET
        url: https://api.honeycomb.io/1/slos/__all__
        headers:
      - name: X-Honeycomb-Team
        value: "{{ 'honeycomb_api_key' | secret }}"
    - external_kind: honeycomb_slo_details
      iterator: '[.dataset_slugs[] as $slug | . + {"opslevel_slug": $slug}]'
      external_id: .id + "-" + .opslevel_slug
      http_polling:
        method: GET
        for_each: honeycomb_slos
        url: https://api.honeycomb.io/1/slos/__all__/{{ honeycomb_slos.id }}?detailed=true
        headers:
        - name: Content-Type
          value: application/json
        - name: X-Honeycomb-Team
          value: "{{ 'honeycomb_api_key' | secret }}"
    ```
    *   **`external_kind`**: A unique identifier for the type of data being extracted.
    *   **`iterator: "."`**: This JQ expression tells OpsLevel to iterate over each item in the Honeycomb API response, treating each as an individual object.
    *   **`external_id: ".id"`**: A JQ expression to select a value that uniquely identifies the SLOs in Honeycomb (e.g., the SLO ID).
    *   **`http_polling`**: This section defines how OpsLevel will actively poll the Honeycomb API.
        *   **`method: GET`**: The HTTP method for the API call.


### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted Honeycomb data to your OpsLevel component properties and relationships.

1.  **Define Transformer**: Configure the transform definition in YAML as follows:

    ```yaml
    ---
    transforms:
    - external_kind: honeycomb_slo_details
      on_component_not_found: skip
      opslevel_kind: service
      opslevel_identifier: ".opslevel_slug"
      properties:
       latency_budget_remaining: ((.budget_remaining * 100 | round / 100) | tostring) + "%"
       latency_slo_compliance: ((.compliance * 100 | round / 100) | tostring) + "%"
       latency_slo_status: ".status"
       latency_target: ((.target_per_million / 10000)| tostring) + "%"

    ```
    *   **`external_kind: honeycomb_slo_details`**: This is mapping the data of the Honey SLO details to the custom properties in OpsLevel.
    *   **`opslevel_kind: service`**: This is mapping the data of the Honeycomb SLOs to the correct component type in OpsLevel (service).
    *   **`on_component_not_found: skip`**: Specifies the custom integration to skip any SLOs that don't match a service in OpsLevel.


### Step 6: Test and Sync the Integration

After configuring both definitions, you can test and activate your integration.

1.  **Run Test**: Use the "Run Test" feature within the custom integration interface. This will execute the API call to Honeycomb, return the actual payload, and allow you to inspect the data, verifying how it maps to properties and which new components will be created.
2.  **Save Configuration**: Save your Extraction and Transform Definitions.
3.  **Observe Components**: Once the sync completes, you will see your SLO data mapped to services in your OpsLevel catalog.
    *   **Managed Properties**: Properties managed by the integration (e.g., Target, Compliance, etc) will be **locked** and cannot be updated directly from the OpsLevel UI or API; updates must come via the integration itself.

### Step 7 (Optional): Visualize data in single value widgets

After configuring custom integration, you can add single value widgets to your service layout as a different way of visualizing the data.

<img width="2543" height="882" alt="image" src="https://github.com/user-attachments/assets/60f6ffba-cae3-4037-b250-bfeff69a342b" />

1.  **Navigate to Customization**: In OpsLevel, go to **Settings > Customization > Service > Layout**.
2.  **+ New Widget**: Add a new `Catalog Data: single value` widget to your layout (can be added to the summary tab, or a new custom tab if desired.
3.  **Configure widget**: Add a title, description, query, value & any style overrides.

   <img width="1204" height="822" alt="image" src="https://github.com/user-attachments/assets/b3b06808-fe0f-40aa-a507-be95cce05afc" />
  
**Query**:
<pre>account
  {
    service (id: $id)
    {
        property (definition: {alias: "property_name"}) 
      {
         
            value
          
      } 
     }
  }</pre>
