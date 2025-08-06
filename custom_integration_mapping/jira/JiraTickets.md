# OpsLevel Custom Integration with Jira: Bringing Jira Tickets into Your Software Catalog

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel to track Jira tickets as components in your software catalog. This powerful feature allows you to extend and customize your catalog by integrating external data sources, even for products not natively supported by OpsLevel.

## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:
*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as will be demonstrated with Jira.

The process involves a two-stage approach:
1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.

## Setup Instructions

### Step 1: Create a Custom Component Type for Jira Tickets in OpsLevel

You'll need to define a new component type in OpsLevel to represent your Jira tickets.

1.  **Navigate to Component Types**: In OpsLevel, go to **Settings > Component Types**.
2.  **Create New Component Type**: Select **+ New Component Type**.
3.  **Define "Jira Ticket" Component Type**:
    *   **Display Name**: Enter `Jira Ticket`.
    *   **Identifier**: The identifier will be auto-generated; you can keep it or change it.
    *   **Description**: Provide helper text (e.g., "Used to track Jira tickets related to services and teams in OpsLevel").
    *   **Customize Icon** (Optional): You can customize the icon for this component type.
    *   Press **Save**.
4.  **Define Custom Properties**: On the Component Edit Page, define the following custom properties:
    *   **Name**: Type `Text` (String).
    *   **Summary**: Type `Text` (String).
    *   **Status**: Type `Text` (String).
    *   **Team Name**: Type `Text` (String). This property will be mapped from a custom field for "Team" in Jira.
    *   **Service Name**: Type `Text` (String). This property will be mapped from a custom field for "Service" in Jira.
    *   **Display Status**: For `Team Name` and `Service Name`, consider hiding them if they are primarily used for mapping relationships and not necessary for direct display to component owners.
5.  **Define Custom Relationships**: Establish relationships to link Jira tickets to existing services and teams in OpsLevel:
    *   **Associated Service**:
        *   **Display Name**: `Associated Service`.
        *   **Identifier**: `associated_service`.
        *   **Allowed Types**: Select `Service`.
        *   **Management Rule**: Set a rule to automatically associate the Jira ticket to a service based on the `Service Name` property. For example, `Jira Ticket` `Service Name` `equals` `Service` `Name`.
    *   **Associated Team**:
        *   **Display Name**: `Associated Team`.
        *   **Identifier**: `associated_team`.
        *   **Allowed Types**: Select `Team`.
        *   **Management Rule**: Set a rule to associate the Jira ticket to a team based on the `Team Name` property. For example, `Jira Ticket` `Team Name` `equals` `Team` `Name`.

### Step 2: Create a Secret in OpsLevel for Jira Authentication

You'll need a secret to store your Jira API token for authentication.

1.  **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2.  **Create New Secret**:
    *   **Name**: `jira_basic_auth_header`.
    *   **Value**: This should be a Base64 encoded string of your Jira user email and API token, in the format `Basic $(echo -n "<user-email>:<jira-api-token>" | base64)`.

### Step 3: Create a Custom Integration Mapping in OpsLevel

This step initiates the custom integration process.

1.  **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2.  **Add Custom Integration**: Select the **Custom** integration option.
3.  **Name the Integration**: You can name it `Jira`. The icon will automatically switch based on the name you choose.

### Step 4: Configure the Extraction Definition

The extraction definition specifies how OpsLevel will pull data from Jira.

1.  **Access Configuration**: Within your custom Jira integration, find the **Extract and Transform Configuration** section.
2.  **Define Extractor**: Configure the extractor definition in YAML as follows:

    ```yaml
    ---
    extractors:
      - external_kind: jira_ticket
        iterator: ".issues"
        external_id: ".id"
        exclude: .fields.statusCategory.name == "Done"
        http_polling:
          method: GET
          url: https://<yourdomain>.atlassian.net/rest/api/3/search/jql?jql=status%20IN%20(%22To%20Do%22%2C%20%22IN%20PROGRESS%22)&maxResults=50&fields=customfield_10001%2Ccustomfield_10070%2CstatusCategory%2Csummary&startAt={{ cursor }}
          headers:
            - name: Accept
              value: application/json
            - name: Authorization
              value: "{{ 'jira_basic_auth_header' | secret }}"
            next_cursor:
            from: payload
            value: if .issues == [] then null else (.startAt + .maxResults)|tostring end              
    ```
    *   **`external_kind: jira_ticket`**: A unique identifier for the type of data being extracted.
    *   **`iterator: ".issues"`**: This JQ expression tells OpsLevel to iterate over each item in the "issues" array within the Jira API response, treating each as an individual object.
    *   **`external_id: ".id"`**: A JQ expression to select a value that uniquely identifies the object in Jira (e.g., the Jira ticket ID).
    *   **`exclude: .fields.statusCategory.name == "Done"`**: This JQ expression serves as an exclusion rule. It will prevent Jira tickets with a status category of "Done" from being pulled into OpsLevel. If a ticket was previously in OpsLevel and its status changes to "Done", this rule will cause it to be automatically deleted from the catalog.
    *   **`http_polling`**: This section defines how OpsLevel will actively poll the Jira API.
        *   **`method: GET`**: The HTTP method for the API call.
        *   **`url: https://<yourdomain>.atlassian.net/rest/api/3/search/jql?...`**: Replace `<yourdomain>` with your Jira domain. This URL defines the JQL query to fetch tickets. The example JQL filters for tickets with "To Do" or "In Progress" statuses and specifies the fields to retrieve, including custom fields like `customfield_10001` (for Team) and `customfield_10070` (for Service).
        *   **`headers`**:
            *   **`Authorization: "{{ 'jira_basic_auth_header' | secret }}"`**: This dynamically pulls the value of the `jira_basic_auth_header` secret you created in Step 2 to authenticate the API call.

### Step 5: Configure the Transformation Definition

The transformation definition maps the extracted Jira data to your OpsLevel component properties and relationships.

1.  **Define Transformer**: Configure the transform definition in YAML as follows:

    ```yaml
    ---
    transforms:
      - external_kind: jira_ticket
        on_component_not_found: create
        opslevel_kind: jira_ticket
        opslevel_identifier: ".key"
        properties:
          name: ".fields.summary"
          summary: ".fields.summary"
          status: ".fields.statusCategory.name"
          team_name: ".fields.customfield_10001.name"
          service_name: ".fields.customfield_10070"
    ```
    *   **`external_kind: jira_ticket`**: This must match the `external_kind` defined in your extraction definition to ensure the correct data is processed.
    *   **`on_component_not_found: create`**: Specifies that if an OpsLevel component matching the `opslevel_identifier` is not found, a new component should be created. Other options include `skip` or `suggest`.
    *   **`opslevel_kind: jira_ticket`**: This must match the identifier of the custom component type you created in Step 1 (`jira_ticket`).
    *   **`opslevel_identifier: ".key"`**: A JQ expression that selects a unique identifier from the extracted Jira data (e.g., the Jira ticket key) to map to an existing OpsLevel component or create a new one. This will become the alias of the OpsLevel component.
    *   **`properties`**: This section defines how specific Jira fields are mapped to the custom properties of your `Jira Ticket` component type.
        *   `name: ".fields.summary"`: Maps the Jira ticket summary to the `Name` property in OpsLevel.
        *   `summary: ".fields.summary"`: Maps the Jira ticket summary to the `Summary` property in OpsLevel.
        *   `status: ".fields.statusCategory.name"`: Maps the Jira ticket status category name to the `Status` property.
        *   `team_name: ".fields.customfield_10001.name"`: Maps the name from Jira's custom field `customfield_10001` (representing the team) to the `Team Name` property.
        *   `service_name: ".fields.customfield_10070"`: Maps the value from Jira's custom field `customfield_10070` (representing the service) to the `Service Name` property.

### Step 6: Test and Sync the Integration

After configuring both definitions, you can test and activate your integration.

1.  **Run Test**: Use the "Run Test" feature within the custom integration interface. This will execute the API call to Jira, return the actual payload, and allow you to inspect the data, verifying how it maps to properties and which new components will be created.
2.  **Save Configuration**: Save your Extraction and Transform Definitions.
3.  **Enable Sync**: Ensure the integration sync is enabled. OpsLevel will automatically pull data daily by default, or you can manually kick off a sync. You can also schedule the sync to run every 1 hour.
4.  **Observe Components**: Once the sync completes, you will see your Jira tickets appear as new `Jira Ticket` components in your OpsLevel catalog.
    *   **Managed Properties**: Properties managed by the integration (e.g., Status, Summary) will be **locked** and cannot be updated directly from the OpsLevel UI or API; updates must come via the integration itself.
    *   **Relationships**: The relationships you defined (Associated Service, Associated Team) will be automatically established. For instance, looking at a Service or Team component will show the inverse relationship, listing associated Jira tickets.

---

## Important Considerations

*   **JQ Expressions**: The system relies on JQ expressions for data extraction and transformation. Leverage JQ for transformations.
*   **Filtering Data**: For large datasets like Jira tickets, utilize the `exclude` parameter in the extraction definition to filter out unwanted data, preventing the catalog from becoming overloaded. Leverage the Jira API parameters for filtering.