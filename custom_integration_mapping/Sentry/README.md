# Sentry custom integration setup: Pull issues from Sentry into your software catalog

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel to track Sentry issues as components in your software catalog.

Additionally here is [video recording](https://us02web.zoom.us/clips/share/Q2Rys1QCRpif30y_aNtf9Q) covering the step by step instructions.

## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:
*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as will be demonstrated with Sentry.

The process involves a two-stage approach:
1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.

## Setup Instructions

### Step 1: Create a Custom Component Type for Sentry Issues in OpsLevel

You'll need to define a new component type in OpsLevel to represent your Sentry issues.

1.  **Navigate to Component Types**: In OpsLevel, go to **Settings > Component Types**.
2.  **Create New Component Type**: Select **+ New Component Type**. [Documentation](https://docs.opslevel.com/docs/components)
3.  **Define "Incident" Component Type**:
    *   **Display Name**: Enter `Sentry Issue`.
    *   **Identifier**: The identifier will be auto-generated; you can keep it or change it.
    *   **Description**: Provide helper text (e.g., "Used to track Sentry issues related to services").
    *   **Customize Icon** (Optional): You can customize the icon for this component type.
    *   Press **Save**.
    <img width="2302" height="991" alt="image" src="https://github.com/user-attachments/assets/2768071a-6802-4c61-aae8-70d566aab7c5" />


4.  **Define Custom Properties**: On the Component Edit Page, define the following custom properties:
    *   **Project Slug**: Type `Array` (String).
    *   **Substatus**: Type `Text` (String).
    *   **URL**: Type `Text` (String).
    <img width="2021" height="1269" alt="image" src="https://github.com/user-attachments/assets/53dabd8e-7c8f-4687-ac5b-bb62209f178c" />



5.  **Define Custom Relationships**: Create a relationship on the Service component type to link Sentry issues to existing services in OpsLevel:
    *   **Sentry Issues**:
        *   **Display Name**: `Sentry Issues`.
        *   **Identifier**: `sentry_issues`.
        *   **Allowed Types**: Select `Sentry Issue`.
        *   **Management Rule**: Set a rule to automatically associate the Sentry issues to a service based on the `Project Slug` matching a Service's alias.
<img width="2305" height="1211" alt="image" src="https://github.com/user-attachments/assets/83b5e9e1-c125-49cb-8d52-3086573dfa27" />


### Step 2: Create a Secret in OpsLevel for Sentry Authentication

You'll need a secret to store your Sentry API token for authentication.

1.  **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2.  **Create New Secret**:
    *   **Name**: `sentry_api_token`.


### Step 3: Create a Custom Integration Mapping in OpsLevel

This step initiates the custom integration process.

1.  **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2.  **Add Custom Integration**: Select the **Custom** integration option.
3.  **Name the Integration**: You can name it `Sentry Issues`.

### Step 4: Configure the Extraction Definition

The extraction definition specifies how OpsLevel will pull data from Sentry.

1.  **Access Configuration**: Within your custom Sentry integration, find the **Extract and Transform Configuration** section.
2.  **Define Extractor**: Configure the extractor definition in YAML as follows:

    ```yaml
    ---
    extractors:
    - external_kind: sentry_project
      iterator: "."
      external_id: ".id"
      exclude: .name | test("production")
      http_polling:
        method: GET
        url: "{% if cursor %}{{cursor}}{% else %}https://sentry.io/api/0/projects/{% endif %}"
        headers:
        - name: Accept
          value: application/json
        - name: Authorization
          value: Bearer {{ 'sentry_api_token' | secret }}
        next_cursor:
          from: header
          value: if .link.next.attributes.results == "true" then .link.next.target_url else null end
    - external_kind: sentry_issue
      iterator: "."
      external_id: ".id"
      http_polling:
        method: GET
        for_each: sentry_project
        url: "{% if cursor %}{{cursor}}{% else %}https://sentry.io/api/0/projects/opslevel/{{ sentry_project.id }}/issues/{% endif %}"
        headers:
        - name: Accept
          value: application/json
        - name: Authorization
          value: Bearer {{ 'sentry_api_token' | secret }}
        next_cursor:
          from: header
          value: if .link.next.attributes.results == "true" then .link.next.target_url else null end
           
    ```
    *   **`external_kind`**: A unique identifier for the type of data being extracted.
    *   **`iterator: ".[]"`**: This JQ expression tells OpsLevel to iterate over each item in the Sentry API response, treating each as an individual object.
    *   **`external_id: ".id"`**: A JQ expression to select a value that uniquely identifies the issues in Sentry (e.g., the Sentry Issue ID).
    *   **`http_polling`**: This section defines how OpsLevel will actively poll the Sentry API.
        *   **`method: GET`**: The HTTP method for the API call.


### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted Sentry data to your OpsLevel component properties and relationships.

1.  **Define Transformer**: Configure the transform definition in YAML as follows:

    ```yaml
    ---
    transforms:
    - external_kind: sentry_issue
      on_component_not_found: create
      opslevel_kind: sentry_issue
      opslevel_identifier: ".id"
      properties:
       name: ".title"
       url: ".permalink"
       substatus: ".substatus"
       project_slug: ".project.slug"

    ```
    *   **`external_kind: sentry_issue`**: This is mapping the data of the Sentry issues to the custom properties in OpsLevel.
    *   **`opslevel_kind: sentry_issue`**: This is mapping the data of the Sentry issues to the correct component type in OpsLevel.
    *   **`on_component_not_found: create`**: Specifies the custom integration to automatically create the Sentry Issue components.


### Step 6: Test and Sync the Integration

After configuring both definitions, you can test and activate your integration.

1.  **Run Test**: Use the "Run Test" feature within the custom integration interface. This will execute the API call to Sentry, return the actual payload, and allow you to inspect the data, verifying how it maps to properties and which new components will be created.
2.  **Save Configuration**: Save your Extraction and Transform Definitions.
3.  **Observe Components**: Once the sync completes, you will see your Sentry Issues appear as new components in your OpsLevel catalog.
    *   **Managed Properties**: Properties managed by the integration (e.g., Substatus, Project Slug) will be **locked** and cannot be updated directly from the OpsLevel UI or API; updates must come via the integration itself.
    *   **Relationships**: The relationships you defined (Sentry Issues) will be automatically established. [Documentation](https://docs.opslevel.com/docs/mapping-integration-data-to-custom-properties)

---

## Important Considerations

*   **JQ Expressions**: The system relies on JQ expressions for data extraction and transformation. Leverage [JQ](https://jqlang.org/manual/v1.6/) for transformations.
*   **Filtering Data**: For large datasets like Sentry issues, utilize the `exclude` parameter in the extraction definition to filter out unwanted data, preventing the catalog from becoming overloaded.
