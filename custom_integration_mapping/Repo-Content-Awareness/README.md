# Repo content awareness: Filter and scope on repo grep check results

This README provides a step-by-step guide to setting up a custom integration mapping in OpsLevel that queries **OpsLevel's own GraphQL API** to read the result of a Repo Grep check and writes that result back onto the component as a tag. This lets teams filter, scope Actions, and scope Campaigns based on repo file content, without external infrastructure.

## Overview

OpsLevel's native filters can match on properties, tags, teams, and domains — but not directly on repo file content or check results. This means an Action, Campaign, or Filter can't natively be scoped to "components that grep-match X in their repo."

This integration closes that gap using the same self-referential pattern as [PII Dependency Awareness](https://github.com/OpsLevel/community-integrations/blob/main/custom_integration_mapping/PII-Dependency-Awareness/README.md): OpsLevel polls its own GraphQL endpoint, reads the result of a **Repo Grep check**, and relays that pass/fail result onto the component as a tag — which can then be filtered on like any other tag.

The process involves the same two-stage approach as any custom integration:
1. **Extract**: Polls OpsLevel's own GraphQL API for every component and the result of a specific check.
2. **Transform**: Writes a tag (e.g. `uses_vault: true`) onto the component if that check passed.

Both stages are configured in YAML.

**Worked example used throughout this README**: detecting whether a service uses HashiCorp Vault via GCP, by checking for `useGcpVault: true` in `deploy/helm/values.yaml`. Swap the check details and tag name for your own use case (e.g. a dependency string in `build.gradle` or `package.json`).

## Setup Instructions

### Step 1: Create a Repo Grep check

1. **Create a Campaign or Scorecard**: Maturity → Campaigns (or Scorecards) → New → Create. Use this as the home for the check below rather than adding it to your main maturity rubric, so it doesn't affect maturity scoring for components it applies to.
2. **Add a Repo Grep check** to that Campaign/Scorecard: Create Check → **Repo Grep**.
3. **Configure**:
   * **Path**: the file to search, e.g. `deploy/helm/values.yaml`
   * **Contents**: `matches regex`, e.g. `useGcpVault:\s*true`
4. **Status**: Set to **Enabled** — the check must actually run for the integration to have a result to poll.
5. Note the check's ID — this is a **base64-encoded GID**, not a plain numeric ID (e.g. `Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpSZXBvR3JlcC80Mzg1MA`). Retrieve it via the OpsLevel API/MCP `list_checks`, or from the check's URL. You'll need it in Step 4.

### Step 2: Create a Secret in OpsLevel for API Authentication

1. **Navigate to Secrets**: In OpsLevel, go to **Settings > Secrets**.
2. **Create New Secret**:
   * **Name**: e.g. `opslevel_api_token`.
   * **Value**: an OpsLevel API Token (Integrations → API Tokens) with read access to Services/Checks and write access to Tags.

### Step 3: Create a Custom Integration Mapping in OpsLevel

1. **Navigate to Integrations**: In OpsLevel, go to **Integrations**.
2. **Add Custom Integration**: Select the **Custom** integration option.
3. **Name the Integration**: e.g. `Repo Content Tag Sync`.

### Step 4: Configure the Extract Definition

```yaml
---
extractors:
- external_kind: opslevel_repo_grep_check
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
    body: '{"query":"query checkresults($endCursor: String) { account { services(after: $endCursor) { nodes { id aliases slug maturityReport { latestCheckResults(ids: [\"YOUR_CHECK_ID_HERE\"]) { check { id name } status } } } pageInfo { endCursor hasNextPage } } } }","variables":{"endCursor":"{{ cursor }}"}}'
    next_cursor:
      from: payload
      value: ".data.account.services.pageInfo.endCursor"
```

* **`external_kind: opslevel_repo_grep_check`**: A unique identifier for this extraction; maps to the transform below.
* **`external_id: ".id"`**: Uses OpsLevel's internal component ID as the unique identifier.
* **`iterator: ".data.account.services.nodes"`**: Walks into the GraphQL response and treats each service as its own record.
* **`http_polling`**: Points at OpsLevel's own GraphQL endpoint. If self-hosted, replace with your instance's own reachable GraphQL endpoint.
* **`body`**: Replace `YOUR_CHECK_ID_HERE` with the base64-encoded check ID from Step 1 (e.g. `Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpSZXBvR3JlcC80Mzg1MA`).
* **`next_cursor`**: Supports pagination beyond the first page of services.

### Step 5: Configure the Transform Definition

```yaml
---
transforms:
- external_kind: opslevel_repo_grep_check
  opslevel_kind: service
  opslevel_identifier: ".slug"
  on_component_not_found: skip
  default_properties:
    tags:
    - |-
      (.maturityReport.latestCheckResults[]
        | select(.check.id == "YOUR_CHECK_ID_HERE")
        | .status == "passed") as $passed
      | {"key": "uses_vault", "value": ($passed | tostring)}
```

* **`opslevel_kind: service`**: Maps extracted records to the correct component type. Repeat this transform block (with a different `opslevel_kind`) if you need to cover other component types.
* **`opslevel_identifier: ".slug"`**: Matches back to the real service by its slug.
* **`on_component_not_found: skip`**: Silently skips any record that doesn't resolve to a real component.
* **The JQ expression**: Finds the result for the specific check ID (again, the base64-encoded GID — replace `YOUR_CHECK_ID_HERE` in both places to match) and writes a tag (`uses_vault` here — rename per your use case) of `"true"` or `"false"` based on whether it passed.

> **Note:** unlike a simple existence-only tag, this transform writes `"false"` explicitly rather than omitting the tag on failure. Decide which behavior you want — omitting the tag on failure (using `select` + `empty` instead of an explicit boolean) keeps only-passing components tagged; writing `"false"` lets you filter for the negative case too.

### Step 6: Test and Sync the Integration

1. **Run Test**: Use the "Run Test" feature. Confirm `Items Extracted` is non-zero and inspect a known test service's output.
2. **Save Configuration**.
3. **Verify**: Check a known component that should pass the grep check — confirm the tag lands as expected — and a known component that should fail it.

### Step 7: Create a Filter and apply it

1. **Create a Filter**: Maturity → Filters → New Filter, scoped to `tag uses_vault equals true`.
2. **Apply the Filter** to any Action, Campaign, or Scorecard you want scoped to only components matching the repo content — e.g. an Action that should only be visible to teams using Vault.

## Extending this pattern

This same extract/transform shape works for any Repo Grep check, not just Vault detection:
* **`build.gradle` / `package.json` dependency checks**: swap the check's path and regex, and the tag name in the transform (e.g. `uses_library_x`).
* **Monorepos**: Repo Grep resolves paths relative to the component's configured sub-path (Directory field), not necessarily true repo root. Confirm this is set correctly per-component before assuming a shared path works across all of them.
