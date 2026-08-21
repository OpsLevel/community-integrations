# PII dependency awareness: Flag and track services that depend on PII-classified components

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel that queries **OpsLevel's own GraphQL API** to detect when a service has a native dependency on a component classified as handling sensitive data (e.g. PII), and writes that back onto the service as a tag. This lets teams see, filter, and check for this exposure directly on the Maturity Report, without external infrastructure.

## Overview

Unlike most custom integrations (which pull data from a third-party system), this one is **self-referential**: OpsLevel polls its own GraphQL endpoint, inspects each service's dependencies, and reconciles a tag based on what it finds. This is useful for any case where you want to derive a signal from a component's *relationships* — something OpsLevel's native Relationship Checks currently cannot do for built-in Service Dependencies (as of this writing, native Dependencies are not treated as a Relationship Definition, so they're excluded from relationship-based filtering and checks).

The process involves the same two-stage approach as any custom integration:
1. **Extract**: Polls OpsLevel's own GraphQL API for every service, its native dependencies, and those dependencies' properties.
2. **Transform**: Evaluates whether any dependency is classified as sensitive, and writes a `has_pii_dependency` tag (`true`/`false`) back onto the service.

Both stages are configured in YAML.

## Setup Instructions

### Step 1: Confirm your classification property

**Confirm the property exists**: On the Component Edit Page, confirm your account has a custom property that classifies a component's data sensitivity (e.g. **Data Classification**, with values like `Public` / `Internal` / `Confidential`).
<img width="1772" height="1282" alt="image" src="https://github.com/user-attachments/assets/571931e6-ea2f-4219-ba2b-54aa1096aefe" />

**Important**: confirm the exact **identifier** of this property (Settings → Custom Properties → Component Type → Custom Property).

Also confirm the exact enum value used for your sensitive classification (e.g. `Public`, `Confidential`) — this must match exactly, including case.

### Step 2: Create a Secret in OpsLevel for API Authentication

1. **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2. **Create New Secret**:
   * **Name**: e.g. `opslevel_api_token`.
   * **Value**: an OpsLevel API Token (Settings → API Tokens) with read access to Services and write access to Tags.

### Step 3: Create a Custom Integration Mapping in OpsLevel

1. **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2. **Add Custom Integration**: Select the **Custom** integration option.
3. **Name the Integration**: e.g. `PII Dependency Tag Sync`.

### Step 4: Configure the Extract Definition

```yaml
---
extractors:
- external_kind: opslevel_service_pii_check
  external_id: ".id"
  iterator: ".data.account.services.nodes"
  http_polling:
    url: "https://app.opslevel.com/graphql"
    method: POST
    headers:
    - name: Authorization
      value: Bearer {{ 'opslevel_api_token' | secret }}
    - name: Content-Type
      value: application/json
    body: '{"query":"query servicesWithDependencies($endCursor: String) { account { services(after: $endCursor) { nodes { id aliases slug dependencies { nodes { properties { nodes { definition { name } value } } } } } pageInfo { endCursor hasNextPage } } } }","variables":{"endCursor":"{{ cursor }}"}}'
    next_cursor:
      from: payload
      value: ".data.account.services.pageInfo.endCursor"
```

* **`external_kind`**: A unique identifier for this extraction.
* **`external_id: ".id"`**: Uses OpsLevel's internal component ID as the unique identifier.
* **`iterator: ".data.account.services.nodes"`**: Walks into the GraphQL response and treats each service as its own record.
* **`http_polling`**: Points at OpsLevel's own GraphQL endpoint. If you are on a self-hosted OpsLevel deployment, replace this URL with your instance's own reachable GraphQL endpoint, not the public SaaS URL.
* **`body`**: The exact query used to fetch services, their native dependencies, and each dependency's properties.
* **`next_cursor`**: Supports pagination beyond the first page of services.

### Step 5: Configure the Transform Definition

```yaml
---
transforms:
- external_kind: opslevel_service_pii_check
  opslevel_kind: service
  opslevel_identifier: ".slug"
  on_component_not_found: skip
  default_properties:
    tags:
    - |-
      (.dependencies.nodes
        | map(.properties.nodes[] | select(.definition.name == "Data Classification") | .value == "\"Confidential\"")
        | any) as $has_confidential
      | {"key": "has_pii_dependency", "value": ($has_confidential | tostring)}
```

* **`opslevel_identifier: ".slug"`**: Matches back to the real service by its slug.
* **`on_component_not_found: skip`**: Silently skips any record that doesn't resolve to a real Service, rather than erroring.
* **The JQ expression**: Walks every dependency's properties, checks whether the classification property (`Data Classification` here — **replace with your account's actual property identifier**, equals the sensitive value (`Confidential` here — **replace with your account's actual enum value**, e.g. `PII`), and produces a `has_pii_dependency` tag of `"true"` or `"false"`.

### Step 6: Test and Sync the Integration

1. **Run Test**: Use the "Run Test" feature. Confirm `Items Extracted` is non-zero and inspect a known test service's output.
2. **Save Configuration**.
3. **Verify**: Check a known service with a PII dependency — confirm the `has_pii_dependency` tag is set to `true`, and a service without one is set to `false` (not left unset).

### Step 7: Track acknowledgment on the Maturity Report

The `has_pii_dependency` tag on its own only tells you *that* a risk exists — it doesn't capture whether anyone has actually reviewed it. Pair it with a **Manual Check**, scoped with a **Filter** to only apply to components where `has_pii_dependency` equals `true`, so the acknowledgment requirement only shows up for services that actually need it:

1. **Create a Filter**: Maturity → Filters → New Filter, scoped to `tag has_pii_dependency equals true`.
2. **Create a Manual Check**: Maturity → Rubric → Add Check → **Manual Check**, with that Filter applied. This requires a component owner to explicitly mark the check complete, giving you a human-driven acknowledgment step rather than another automatically-derived signal.
