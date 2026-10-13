# Dependencx Filter: Filter Components by Dependency Type

This is based on the PII Dependency Awareness integration.
This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel that queries **OpsLevel's own GraphQL API** to detect when a service has a native dependency on a component whose type is "Service" or "External Service", and writes that back onto the service as a tag.
This lets teams see and filter on these dependencies to e.g. apply specific campaigns.


## Overview

Unlike most custom integrations (which pull data from a third-party system), this one is **self-referential**: OpsLevel polls its own GraphQL endpoint, inspects each service's dependencies, and reconciles a tag based on what it finds. This is useful for any case where you want to derive a signal from a component's *relationships* — something OpsLevel's native Relationship Checks currently cannot do for built-in Service Dependencies (as of this writing, native Dependencies are not treated as a Relationship Definition, so they're excluded from relationship-based filtering and checks).

The process involves the same two-stage approach as any custom integration:
1. **Extract**: Polls OpsLevel's own GraphQL API for every service, its native dependencies, and those dependencies' component types.
2. **Transform**: Evaluates whether any dependency is of type "Service" or "External Service", and writes a `has_external_dependency` / `has_internal_dependency` tag (`true`/`false`) back onto the service.

Both stages are configured in YAML.

## Setup Instructions

### Step 1: Define which types you want to filter for

Note the component types you want to filter for. In this example, we will filter for "Service" and "External Service".

### Step 2: Create a Secret in OpsLevel for API Authentication

1. **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2. **Create New Secret**:
    * **Name**: e.g. `opslevel_api_token`.
    * **Value**: an OpsLevel API Token (Settings → API Tokens) with read access to Services and write access to Tags.

### Step 3: Create a Custom Integration Mapping in OpsLevel

1. **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2. **Add Custom Integration**: Select the **Custom** integration option.
3. **Name the Integration**: e.g. `OpsLevel_Dependency_Discovery`.

### Step 4: Configure the Extract Definition

```yaml
---
extractors:
  - external_kind: opslevel_dependency_discovery
    iterator: ".data.account.services.nodes"
    external_id: ".id"
    http_polling:
      method: POST
      url: https://app.opslevel.com/graphql
      headers:
        - name: Authorization
          value: Bearer {{ 'opslevel_api_token' | secret }}
        - name: Accept
          value: application/json
        - name: Content-Type
          value: application/json
      body: '{"query":"query servicesWithDependencies($endCursor: String) { account { services(after: $endCursor) { nodes { id aliases slug dependencies { nodes { type { name } } } } pageInfo { endCursor hasNextPage } } } }","variables":{"endCursor":"{{ cursor }}"}}'
      next_cursor:
        from: payload
        value: ".data.account.services.pageInfo.endCursor"

```

* **`external_kind`**: A unique identifier for this extraction.
* **`external_id: ".id"`**: Uses OpsLevel's internal component ID as the unique identifier.
* **`iterator: ".data.account.services.nodes"`**: Walks into the GraphQL response and treats each service as its own record.
* **`http_polling`**: Points at OpsLevel's own GraphQL endpoint. If you are on a self-hosted OpsLevel deployment, replace this URL with your instance's own reachable GraphQL endpoint, not the public SaaS URL.
* **`body`**: The exact query used to fetch services, their native dependencies, and each dependency's component type.
* **`next_cursor`**: Supports pagination beyond the first page of services.

### Step 5: Configure the Transform Definition

```yaml
---
transforms:
  - external_kind: opslevel_dependency_discovery
    opslevel_kind: service
    opslevel_identifier: ".slug"
    on_component_not_found: skip
    default_properties:
      tags:
        - |-
          .dependencies.nodes
            | any(.type.name? == "Service") as $has_internal_dependency
            | any(.type.name? == "External Service") as $has_external_dependency
          | [
          {"key": "has_internal_dependency", "value": ($has_internal_dependency | tostring)},
          {"key": "has_external_dependency", "value": ($has_external_dependency | tostring)}
          ]
```

* **`external_kind: opslevel_dependency_discovery`**: This maps the extracted data to the transform below.
* **`opslevel_kind: service`**: This maps the extracted records to the correct component type in OpsLevel (service).
* **`opslevel_identifier: ".slug"`**: Matches back to the real service by its slug.
* **`on_component_not_found: skip`**: Silently skips any record that doesn't resolve to a real Service, rather than erroring.
* **The JQ expression**: Walks every dependency type, checks whether `.type.name` equals `Service` or `External Service`, and produces a `has_internal_dependency` / `has_external_dependency` tag of `"true"` or `"false"`. If you adapt this pattern to other component types, also rename the tags so they still reflect what they actually mean.

### Step 6: Test and Sync the Integration

1. **Run Test**: Use the "Run Test" feature. Confirm `Items Extracted` is non-zero and inspect a known test service's output.
2. **Save Configuration**.
3. **Verify**: Check a known service with the wanted dependencies  — confirm the `has_internal_dependency` / `has_external_dependency` tag is set to `true`, and a service without one is set to `false` (not left unset).

### Step 7: Use the tags in filters or campaigns

1. **Create a Filter**: Maturity → Filters → New Filter, scoped to `tag has_internal_dependency equals true`.
