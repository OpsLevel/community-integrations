# Pull Wiz issues into your OpsLevel catalog

A **pull**-based custom integration that imports Wiz **Issues** as components —
the same thing OpsLevel's [built-in Wiz
integration](https://docs.opslevel.com/docs/wiz-integration) does, assembled by
hand out of the definitions the product publishes. OpsLevel polls the Wiz
GraphQL API on a schedule; it's all YAML, with no code to run or host. For a
push-based alternative against the same API, see [`../issues/`](../issues/).

## Do you need this?

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

## Start from the published definitions

OpsLevel publishes the extract and transform definitions its own Wiz integration
runs. Don't retype them — download them:

```bash
curl -O https://app.opslevel.com/integration_templates/wiz/default_extract_definition.yml
curl -O https://app.opslevel.com/integration_templates/wiz/default_transform_definition.yml
```

*   **`default_extract_definition.yml`** — the OAuth client-credentials block, and a paginated GraphQL query against Wiz's `issuesV2` API that pulls every `OPEN` and `IN_PROGRESS` issue, excluding `INFORMATIONAL` severity.
*   **`default_transform_definition.yml`** — the mapping from a Wiz issue onto a component's name, aliases, tags and properties.

These are the live files the product loads at boot, so they can't drift from what
the built-in integration does — which is why this guide links them instead of
keeping a copy here. What they don't carry is the component type, the secrets
and the relationship rule; those are the steps below.

## Step 1: Create a Wiz service account

1.  In Wiz, go to **Settings → Access Management → Service Accounts**, and click **Add Service Account**.
2.  Set **Type** to **Custom Integration (GraphQL API)**.
3.  Leave **Projects** empty to sync your whole tenant, or select up to 50 projects to limit what OpsLevel can see.
4.  Leave **Expiration** empty — syncs start failing once the service account expires.
5.  Under **API Scopes**, select `read:issues`. That's the only scope needed.
6.  Copy the **Client ID** and **Client Secret**. Wiz only shows the secret once.

You also need your tenant's **API Endpoint URL**: profile icon → **Tenant Info**
→ **API Endpoint URL**. It looks like `https://api.us1.app.wiz.io/graphql`. Make
sure the URL you use ends in `/graphql` — some Wiz screens show it without.

## Step 2: Store the credentials as OpsLevel secrets

Go to **Settings → Secrets** and create two secrets: **`wiz_client_id`** and
**`wiz_client_secret`**.

## Step 3: Create the component type for Wiz issues

The built-in integration ships a **Wiz Issue** component type, which isn't
published, so create your own: **Components → Manage Types → + New Component
Type**. Give it the identifier **`wiz_issue`** so the transform definition's
`opslevel_kind` works unchanged.

Then add a property definition for each row below — or just the subset you care
about, deleting the rest from the transform definition's `properties` block.

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

Two settings worth copying from the built-in type: turn **maturity off** (rubric
checks against security issues aren't meaningful), and render `description` and
`remediation` as markdown widgets on the **Summary** tab, hidden from the
property list. See [UI
Customization](https://docs.opslevel.com/docs/ui-customization).

## Step 4: Create the custom integration

In OpsLevel, go to **Integrations → + New Integration**, pick **Custom**, and
name it something like `Wiz Issues`.

## Step 5: Configure the extract definition

Paste `default_extract_definition.yml` into the **Extract and Transform
Configuration** section of your integration, then make three edits.

Point `oauth.token_url` at your tenant's authentication endpoint (see the table
above), and swap the credential placeholders for your secrets:

```yaml
---
oauth:
  grant_type: client_credentials
  token_url: https://auth.app.wiz.us/oauth/token       # <- was https://auth.app.wiz.io/oauth/token
  client_id: "{{ 'wiz_client_id' | secret }}"          # <- was REPLACE_WITH_CLIENT_ID
  client_secret: "{{ 'wiz_client_secret' | secret }}"  # <- was REPLACE_WITH_CLIENT_SECRET
  extra_params:
    audience: wiz-api
```

Then replace `REPLACE_WITH_BASE_URL` in `http_polling.url` with your tenant's API
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

Leave everything else alone: the rest of the file is the GraphQL query,
cursor-based pagination via `next_cursor`, and a `rate_limit` handler for Wiz's
429s. Don't drop `extra_params.audience: wiz-api` either — Wiz's token endpoint
requires it.

For a field-by-field reference, see [Setting Up a Pull
Configuration](https://docs.opslevel.com/docs/setting-up-a-pull-configuration-for-your-customizable-data-mapping).

## Step 6: Configure the transform definition

Paste `default_transform_definition.yml` in as-is. If you gave your component
type an identifier other than `wiz_issue` in Step 3, change `opslevel_kind` to
match, and delete any `properties` entries you didn't create a definition for.

Two parts to know before you customize it:

*   **`opslevel_identifier: '"wiz:" + .id'`** and the matching **`aliases`** entry give every issue a `wiz:<issue id>` alias, so re-syncs update the same component instead of creating duplicates.
*   **`on_component_not_found: create`** creates issues as components automatically. Switch to `suggest` to route them through **Catalog → Detected Components** for review instead.

## Step 7: Link issues back to the services that own the affected resources

The transform definition puts the affected cloud resource's identifier on each
issue as a `cloud.service` tag. Turning that tag into a real relationship is a
rule on your component type, not something the transform definition can do.

On your `wiz_issue` component type, add a relationship definition — identifier
`affected_component`, name **Affected Component**, allowed type `service` — with
a management rule matching the issue's `cloud.service` tag against a service
**alias**. See [Relationship
Definitions](https://docs.opslevel.com/docs/relationship-definitions).

For the links to land, add the cloud resource identifier as an alias on the
service that owns it. Issues whose resource identifier matches no service alias
still import — they just aren't attached to a service yet.

## Step 8: Test and sync

Use **Run Test** before you save: it makes the real call to Wiz and shows how the
payload maps to properties and components. Then save both definitions, and your
Wiz issues appear as components once the sync completes.

Two things to expect afterwards:

*   Properties written by the integration are **locked** in the UI and API — updates have to come from the integration.
*   Polled objects are deleted once a sync stops returning them, which is what makes resolved Wiz issues drop out of your catalog. Don't add `expires_after_days` to a polling extractor — OpsLevel rejects the combination, precisely because it's redundant here.

## Troubleshooting

| Symptom | Likely cause |
| :------ | :----------- |
| `401` from the token endpoint | Wrong `token_url` for your tenant, a wrong or expired service account secret, or a missing `audience: wiz-api` in `extra_params` |
| `404` or an HTML response from the polling URL | Your API endpoint URL is missing the `/graphql` path |
| GraphQL errors about unknown fields | Your Wiz tenant is on an API version that doesn't have every field the query selects — trim the selection set in `http_polling.body` |
| Components created but properties empty | Property definition slugs on your component type don't match the keys in the transform definition's `properties` block |
| No **Affected Component** relationships | Missing management rule on the component type (Step 7), or no service carries the resource identifier as an alias |
