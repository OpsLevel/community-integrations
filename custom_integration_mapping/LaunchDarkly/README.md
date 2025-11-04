# OpsLevel Custom Integration with LaunchDarkly: Pull feature flags from LaunchDarkly into your software catalog

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel to import LaunchDarkly feature flags as components in your software catalog.

## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:
*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as will be demonstrated with LaunchDarkly.

The process involves a two-stage approach:
1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.

## Setup Instructions

### Step 1: Create a Custom Component Type for LaunchDarkly Feature Flags in OpsLevel

You'll need to define a new component type in OpsLevel.

1.  **Navigate to Component Types**: In OpsLevel, go to **Settings > Component Types**.
2.  **Create New Component Type**: Select **+ New Component Type**. [Documentation](https://docs.opslevel.com/docs/components)
3.  **Define "Feature Flag" Component Type**:
    *   **Display Name**: Enter `Feature Flag`.
    *   **Identifier**: The identifier will be auto-generated; you can keep it or change it.
    *   **Description**: Provide helper text (e.g., "Used to track LaunchDarkly feature flags related to services").
    *   **Customize Icon** (Optional): You can customize the icon for this component type.
    *   Press **Save**.
    <img width="2300" height="1101" alt="image" src="https://github.com/user-attachments/assets/8ad5d338-77eb-4fc1-ba5e-84733bcf7ef2" />





4.  **Define Custom Properties**: On the Component Edit Page, define the following custom properties:
    *   **Code Reference Repos**: Type `Array` (String).
    *   **Archived**: Type `Boolean` (String).
    *   **Deprecated**: Type `Boolean` (String).
    *   **Maintainer Email**: Type `Text` (String).
    *   **Temporary**: Type `Boolean` (String).
    *   **Created At**: Type `Text` (String).
    <img width="2047" height="1223" alt="image" src="https://github.com/user-attachments/assets/cbc1ea49-4a04-461b-8c4f-4f865af790d8" />





5.  **Define Custom Relationships**: Establish relationships to link LaunchDarkly feature flag to existing services and teams in OpsLevel:
    *   **Service**:
        *   **Display Name**: `Service`.
        *   **Identifier**: `ff_service`.
        *   **Allowed Types**: Select `Service`.
        *   **Management Rule**: Set a rule to automatically associate the LaunchDarkly feature flags to a service based on the `Code Reference Repos` array.
<img width="1773" height="1264" alt="image" src="https://github.com/user-attachments/assets/626b4bcd-05f2-499a-a76c-00fc5308a26e" />




### Step 2: Create a Secret in OpsLevel for LaunchDarkly Authentication

You'll need a secret to store your LaunchDarkly API token for authentication.

1.  **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2.  **Create New Secret**:
    *   **Name**: `launchdarkly_api_key`.


### Step 3: Create a Custom Integration Mapping in OpsLevel

This step initiates the custom integration process.

1.  **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2.  **Add Custom Integration**: Select the **Custom** integration option.
3.  **Name the Integration**: You can name it `LaunchDarkly Feature Flags`.

### Step 4: Configure the Extraction Definition

The extraction definition specifies how OpsLevel will pull data from LaunchDarkly.

1.  **Access Configuration**: Within your custom LaunchDarkly integration, find the **Extract and Transform Configuration** section.
2.  **Define Extractor**: Configure the extractor definition in YAML as follows:

    ```yaml
    ---
    extractors:
      - external_kind: launchdarkly_projects
        external_id: ".key"
        iterator: ".items"
        http_polling:
          method: GET
          url: https://app.launchdarkly.com/api/v2/projects
          headers:
          - name: Authorization
            value: "{{ 'launchdarkly_api_key' | secret }}"
     - external_kind: launchdarkly_feature_flags
       external_id: ".key"
       iterator: ".items"
       http_polling:
         for_each: launchdarkly_projects
         method: GET
         url: https://app.launchdarkly.com/api/v2/flags/{{ launchdarkly_projects.key }}?expand=codeReferences
         headers:
         - name: Authorization
           value: "{{ 'launchdarkly_api_key' | secret }}"
    ```
    *   **`external_kind: launchdarkly_projects & launchdarkly_feature_flags`**: A unique identifier for the type of data being extracted (LaunchDarkly projects & feature flags).
    *   **`iterator: ".items"`**: This JQ expression tells OpsLevel to iterate over each item in the LaunchDarkly API response, treating each as an individual object.
    *   **`external_id: ".key"`**: A JQ expression to select a value that uniquely identifies the projects/feature flags in LaunchDarkly.
    *   **`http_polling`**: This section defines how OpsLevel will actively poll the LaunchDarkly API.
        *   **`method: GET`**: The HTTP method for the API call.


### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted LaunchDarkly data to your OpsLevel component properties and relationships.

1.  **Define Transformer**: Configure the transform definition in YAML as follows:

    ```yaml
    ---
    transforms:
      - external_kind: launchdarkly_feature_flags
        on_component_not_found: create
        opslevel_kind: feature_flag
        opslevel_identifier: ".key"
        properties:
          name: ".name"
          archived: ".archived"
          deprecated: ".deprecated"
          temporary: ".temporary"
          maintainer_email: "._maintainer.email"
          created_at: ".creationDate"
          code_reference_repos: ".codeReferences.items[].repositoryName"
    ```
    *   **`external_kind: launchdarkly_feature_flags`**: This is mapping the data of the LaunchDarkly feature flags to the custom properties in OpsLevel.
    *   **`on_component_not_found: create`**: Specifies that if an OpsLevel component matching the `opslevel_identifier` is not found, a new feature flag should be created. Other options include `skip` or `suggest`.


### Step 6: Test and Sync the Integration

After configuring both definitions, you can test and activate your integration.

1.  **Run Test**: Use the "Run Test" feature within the custom integration interface. This will execute the API call to LaunchDarkly, return the actual payload, and allow you to inspect the data, verifying how it maps to properties and which new components will be created.
2.  **Save Configuration**: Save your Extraction and Transform Definitions.
3.  **Observe Components**: Once the sync completes, you will see your LaunchDarkly feature flags appear as new `Feature Flag` components in your OpsLevel catalog.
    *   **Managed Properties**: Properties managed by the integration (e.g., Archived, Maintainer email) will be **locked** and cannot be updated directly from the OpsLevel UI or API; updates must come via the integration itself.
    *   **Relationships**: The relationships you defined (Service) will be automatically established. [Documentation](https://docs.opslevel.com/docs/mapping-integration-data-to-custom-properties)

---

## Important Considerations

*   **JQ Expressions**: The system relies on JQ expressions for data extraction and transformation. Leverage [JQ](https://jqlang.org/manual/v1.6/) for transformations.
*   **Filtering Data**: For large datasets like LaunchDarkly feature flags, utilize the `exclude` parameter in the extraction definition to filter out unwanted data, preventing the catalog from becoming overloaded. Leverage the LaunchDarkly API parameters for filtering.
