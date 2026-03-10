
```graphql
mutation create_componentType_Jira_Ticket($input: ComponentTypeInput!) {
  componentTypeCreate(input: $input) {
    componentType {
      id
      name
    }
    errors {
      message
      path
    }
  }
}
```

Query Variables

```json
{
  "input": {
    "name": "Jira Ticket",
    "alias": "jira_ticket",
    "description": "Track open Jira Tickets within OpsLevel and the related Components and Teams.",
    "icon": {
      "name": "PhTicket",
      "color": "#ffc53d"
    },
    "properties": [
      {
        "name": "Service Name",
        "alias": "service_name",
        "schema": "{\"type\": \"string\"}",
        "description": "Service Name defined in Jira",
        "allowedInConfigFiles": false,
        "propertyDisplayStatus": "hidden"
      },
      {
        "name": "Team Name",
        "alias": "team_name",
        "schema": "{\"type\": \"string\"}",
        "description": "Team Name defined in Jira",
        "allowedInConfigFiles": false,
        "propertyDisplayStatus": "hidden"
      },
      {
        "name": "Summary",
        "alias": "summary",
        "schema": "{\"type\": \"string\"}",
        "description": "Ticket Summary",
        "allowedInConfigFiles": false,
        "propertyDisplayStatus": "visible"
      },
      {
        "name": "Status",
        "alias": "status",
        "schema": "{\"type\": \"string\"}",
        "description": "Ticket Status",
        "allowedInConfigFiles": false,
        "propertyDisplayStatus": "visible"
      },
      {
        "name": "URL",
        "alias": "url",
        "schema": "{\"type\": \"string\", \"format\": \"uri\"}",
        "description": "Ticket Status",
        "allowedInConfigFiles": false,
        "propertyDisplayStatus": "visible"
      }
    ]
  }
}
```