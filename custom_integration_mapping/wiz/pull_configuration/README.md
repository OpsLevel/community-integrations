# Wiz custom integration setup: Pull cloud security issues from Wiz into your software catalog

This README walks through building a **pull**-based custom integration that
imports Wiz **Issues** into your OpsLevel catalog as components — the same thing
OpsLevel's [built-in Wiz integration](https://docs.opslevel.com/docs/wiz) does,
but assembled by hand out of the definitions the product publishes.

## Do you actually need this?

Probably not. If your Wiz tenant authenticates against Wiz's commercial endpoint
(`https://auth.app.wiz.io/oauth/token`), install the built-in integration
instead — **Integrations → + New Integration → Wiz** — and skip this guide
entirely. You get the component type, the property schema, the relationship
rules and the daily sync with no YAML at all.

Build it by hand when your tenant authenticates somewhere the built-in
integration can't reach:

| Tenant | Authentication endpoint |
| :----- | :---------------------- |
| Wiz for Gov | `https://auth.app.wiz.us/oauth/token` |
| Wiz on AWS GovCloud | `https://auth.gov.wiz.io/oauth/token` |
| Older tenants still on Wiz's Auth0 endpoint | `https://auth.wiz.io/oauth/token` |

## Overview of Custom Integrations

OpsLevel's custom integration system supports two patterns:

*   **Push Integrations**: Where external systems send data directly to OpsLevel via webhooks. See [`../issues/`](../issues/) for a script-driven push example against the same Wiz API.
*   **Pull Integrations**: Where OpsLevel actively pulls data from an external API, as demonstrated here.

The process involves a two-stage approach:

1.  **Extract**: Defines how to retrieve your data, including HTTP polling settings, authentication, and data extraction rules.
2.  **Transform**: Defines how to map the extracted data to your OpsLevel catalog properties, create component types, and establish relationships between different objects.

Both stages are configured in YAML, requiring no coding and allowing for configuration-driven integrations.

## Start from the published definitions

OpsLevel publishes the extract and transform definitions its own Wiz integration
runs. Don't retype them — download them:

```bash
curl -O https://app.opslevel.com/integration_templates/wiz/default_extract_definition.yml
curl -O https://app.opslevel.com/integration_templates/wiz/default_transform_definition.yml
```

No authentication needed. These are the live files the product loads at boot, so
they can't drift from what the integration actually does — which is why this
guide links them instead of keeping a copy here.

*   **`default_extract_definition.yml`** — the OAuth client-credentials block, and a paginated GraphQL query against Wiz's `issuesV2` API that pulls every `OPEN` and `IN_PROGRESS` issue, excluding `INFORMATIONAL` severity.
*   **`default_transform_definition.yml`** — the mapping from a Wiz issue onto a component's name, aliases, tags and properties.

## Setup Instructions

### Step 1: Create a Wiz service account

1.  In Wiz, go to **Settings → Access Management → Service Accounts**, and click **Add Service Account**.
2.  Set **Type** to **Custom Integration (GraphQL API)**.
3.  Leave **Projects** empty to sync your whole tenant, or select up to 50 projects to limit what OpsLevel can see.
4.  Leave **Expiration** empty — syncs start failing once the service account expires.
5.  Under **API Scopes**, select `read:issues`. That's the only scope needed.
6.  Copy the **Client ID** and **Client Secret**. Wiz only shows the secret once.

You also need your tenant's **API Endpoint URL**: profile icon → **Tenant Info**
→ **API Endpoint URL**. It looks like `https://api.us1.app.wiz.io/graphql`. Make
sure the URL you use ends in `/graphql` — some Wiz screens show it without.

### Step 2: Create Secrets in OpsLevel for Wiz authentication

Go to **Settings → Secrets** and create two secrets:

*   **`wiz_client_id`** — your service account's client ID.
*   **`wiz_client_secret`** — your service account's client secret.

### Step 3: Create the component type for Wiz issues

The built-in integration ships a **Wiz Issue** component type. That one isn't
published, so create your own: **Components → Manage Types → + New Component
Type**.

Give it the identifier **`wiz_issue`** and the transform definition's
`opslevel_kind` works unchanged. Then add a property definition for each row
below — or just the subset you care about, and delete the rest from the
transform definition's `properties` block.

| Property | Display Name | Schema | Description |
| :------- | :----------- | :----- | :---------- |
| `cloud_account_id` | Cloud Account Id | string | The identifier of the cloud account or subscription that owns the resource |
| `cloud_account_name` | Cloud Account Name | string | The name of the cloud account or subscription that owns the resource |
| `cloud_console_url` | Cloud Console Url | string (uri) | A link to the resource in the cloud provider's console |
| `cloud_platform` | Cloud Platform | string | The cloud platform hosting the resource, such as AWS, Azure or GCP |
| `cloud_provider_id` | Cloud Provider Id | string | The cloud provider's identifier for the resource |
| `compliance` | Compliance Mappings | array of object | The compliance framework, category and requirement the issue maps to |
| `description` | Description | string | The description of the rule or control that raised the issue |
| `detected_at` | Detected At | string (date-time) | The date and time Wiz first detected the issue |
| `due_at` | Due At | string (date-time) | The date and time the issue is due to be resolved |
| `frameworks` | Compliance Frameworks | array of string | The compliance frameworks the issue maps to |
| `issue_status` | Status | string | The current status of the issue in Wiz |
| `issue_type` | Issue Type | string | The type of issue Wiz detected, such as a misconfiguration or a threat detection |
| `last_seen_at` | Last Seen At | string (date-time) | The date and time Wiz last updated the issue |
| `region` | Region | string | The cloud region the resource lives in |
| `remediation` | Remediation | string | The recommended steps to resolve the issue |
| `resolved_at` | Resolved At | string (date-time) | The date and time the issue was resolved |
| `resource_name` | Affected Resource | string | The name of the cloud resource the issue was detected on |
| `resource_status` | Resource Status | string | The status of the cloud resource the issue was detected on |
| `resource_type` | Resource Type | string | The type of the cloud resource the issue was detected on |
| `risks` | Risks | array of string | The risks associated with the rules that raised the issue |
| `rules` | Detection Rules | array of string | The names of the Wiz rules or controls that raised the issue |
| `service_tickets` | Tickets | array of object | The tickets Wiz opened for the issue in external ticketing systems |
| `severity` | Severity | string | The severity Wiz assigned to the issue |
| `status_changed_at` | Status Changed At | string (date-time) | The date and time the status of the issue last changed |
| `wiz_id` | Wiz Issue Id | string | The Wiz identifier for this issue |
| `wiz_projects` | Wiz Projects | array of object | The Wiz projects the issue belongs to |
A couple of settings worth copying from the built-in type:

*   Turn **maturity off** for the type — rubric checks against security issues aren't meaningful.
*   Render `description` and `remediation` as markdown widgets on the **Summary** tab, and hide them from the property list. See [UI Customization](https://docs.opslevel.com/docs/ui-customization).

### Step 4: Create the Custom Integration

1.  In OpsLevel, go to **Integrations**.
2.  Select the **Custom** integration option.
3.  Name it something like `Wiz Issues`.

### Step 5: Configure the Extract Definition

Paste `default_extract_definition.yml` into the **Extract and Transform
Configuration** section of your integration, then make three edits.

**Point `oauth.token_url` at your tenant's authentication endpoint** (see the
table at the top of this README), and **swap the credential placeholders for
your secrets**:

```yaml
---
oauth:
  grant_type: client_credentials
  token_url: https://auth.app.wiz.us/oauth/token   # <- your tenant's endpoint
  client_id: "{{ 'wiz_client_id' | secret }}"      # <- was REPLACE_WITH_CLIENT_ID
  client_secret: "{{ 'wiz_client_secret' | secret }}"  # <- was REPLACE_WITH_CLIENT_SECRET
  extra_params:
    audience: wiz-api
```

**Replace `REPLACE_WITH_BASE_URL`** in `http_polling.url` with your tenant's API
endpoint URL:

```yaml
extractors:
- external_kind: wiz_issue
  external_id: ".id"
  iterator: ".data.issues.nodes"
  exclude: .severity == "INFORMATIONAL"
  http_polling:
    url: https://api.us1.app.wiz.io/graphql       # <- was REPLACE_WITH_BASE_URL
    method: POST
    # ... leave the rest of the downloaded file as-is
```

Leave everything else alone. The rest of the file is the GraphQL query, the
cursor-based pagination via `next_cursor`, and a `rate_limit` handler for Wiz's
429s.

*   **`external_kind`**: The identifier the transform definition matches on. Keep it `wiz_issue`.
*   **`external_id: ".id"`**: The Wiz issue ID, which makes each component stable across syncs.
*   **`iterator`**: A JQ expression selecting the array of issues out of the GraphQL response.
*   **`exclude`**: A JQ predicate dropping `INFORMATIONAL` issues before they reach the transform.
*   **`extra_params.audience: wiz-api`**: Required by Wiz's token endpoint. Don't remove it.

For a field-by-field reference, see [Setting Up a Pull Configuration](https://docs.opslevel.com/docs/setting-up-a-pull-configuration-for-your-customizable-data-mapping) and [Authenticating with OAuth](https://docs.opslevel.com/docs/setting-up-a-pull-configuration-for-your-customizable-data-mapping#oauth).

### Step 6: Configure the Transformation Definition

Paste `default_transform_definition.yml` in as-is. If you gave your component
type an identifier other than `wiz_issue` in Step 3, change `opslevel_kind` to
match, and delete any `properties` entries you didn't create a definition for.

The parts worth understanding before you customize it:

*   **`opslevel_identifier: '"wiz:" + .id'`** and the matching **`aliases`** entry: every issue gets a `wiz:<issue id>` alias, so re-syncs update the same component instead of creating duplicates.
*   **`on_component_not_found: create`**: issues are created as components automatically. Switch to `suggest` to route them through **Catalog → Detected Components** for review instead.
*   **`default_properties.name`**: names each component after the rule that raised the issue and the resource it was raised on — for example `Publicly exposed storage bucket on prod-assets`.
*   **`default_properties.tags`**: sets `source`, `wiz_severity`, `wiz_status` and `wiz_issue_type` so you can filter and group issues anywhere OpsLevel supports tag filters — plus `cloud.service`, which is what links an issue back to a service (see Step 7).

### Step 7: Link issues back to the services that own the affected resources

The transform definition puts the affected cloud resource's identifier on each
issue as a `cloud.service` tag. Turning that tag into a real relationship is a
rule on your component type, not something the transform definition can do.

On your `wiz_issue` component type, add a relationship definition — call it
**Affected Component**, allowed type `service` — with a management rule matching
the issue's `cloud.service` tag against a service **alias**. See [Relationship
Definitions](https://docs.opslevel.com/docs/relationship-definitions).

For the links to land, add the cloud resource identifier as an alias on the
service that owns it. Issues whose resource identifier matches no service alias
still import — they just aren't attached to a service yet.

### Step 8: Test and sync

1.  **Run Test**: Use the **Run Test** feature in the custom integration interface. It executes the real call to Wiz, returns the payload, and shows how it maps to properties and components — do this before you save.
2.  **Save Configuration**: Save both definitions.
3.  **Check your catalog**: Once the sync completes, your Wiz issues appear as components of your new type.
    *   **Managed Properties**: Properties written by the integration are **locked** in the UI and API — updates have to come from the integration.
    *   **Removal**: Polled objects are deleted once a sync stops returning them, which is what makes resolved Wiz issues drop out of your catalog. Don't add `expires_after_days` to a polling extractor — OpsLevel rejects the combination, precisely because it's redundant here.

## Troubleshooting

| Symptom | Likely cause |
| :------ | :----------- |
| `401` from the token endpoint | Wrong `token_url` for your tenant, a wrong or expired service account secret, or a missing `audience: wiz-api` in `extra_params` |
| `404` or an HTML response from the polling URL | Your API endpoint URL is missing the `/graphql` path |
| GraphQL errors about unknown fields | Your Wiz tenant is on an API version that doesn't have every field the query selects — trim the selection set in `http_polling.body` |
| Components created but properties empty | Property definition slugs on your component type don't match the keys in the transform definition's `properties` block |
| No **Affected Component** relationships | Missing management rule on the component type (Step 7), or no service carries the resource identifier as an alias |
