# GitHub Repositories → OpsLevel Custom Integration

This guide sets up a **pull** custom integration that reads every repository in a GitHub organization and creates
one **GitHub Repository** component per repo in OpsLevel, with repo metadata as custom properties. It also computes
a **Risk Priority** (P1–P4) from two GitHub custom properties, `data_classification` and `external_interface_type`,
and grades the repositories on a risk-based scorecard.

OpsLevel doesn't run maturity checks on the repository object itself, so a component per repository is what makes
repository-level checks possible.

## Overview

```text
GitHub REST API: GET /orgs/<org>/repos   (polled by OpsLevel on a schedule)
  ↓
OpsLevel Custom Integration (pull)
  ↓
Extractor YAML: one record per repo (external_kind github_repos)
  ↓
Transform YAML: properties + computed risk_priority
  ↓
"GitHub Repository" components (one per repo)
  ↓
Filters + "(Use Case) Security - GitHub Repository Risk" scorecard
```

Nothing runs on your infrastructure: OpsLevel calls the GitHub API with a token stored as an OpsLevel secret.

## Two ways to set it up

| Option | Use it when |
|---|---|
| **[Terraform](terraform/)** | You want everything (component type, secret, integration, filters, scorecard) created in one `apply` and kept in code. Also includes an alternative package that writes the metadata onto your existing **Services** instead of creating new components. |
| **Step by step** (this guide) | You want to see and adjust each piece. Two stdlib-only Python scripts create the component type and the scorecard through the GraphQL API; the integration is pasted in the UI. |

## Files

| File | What it is |
|---|---|
| [`extract_definition.yaml`](extract_definition.yaml) | Extractor: polls `GET /orgs/<your_github_org>/repos`, following every page |
| [`transform_definition.yaml`](transform_definition.yaml) | Transform: one `github_repository` component per repo, 14 properties, computed Risk Priority |
| [`example_github_api_response.json`](example_github_api_response.json) | Sample GitHub response (3 fictional repos) to test the transform's jq locally |
| [`scripts/create_github_repository_type.py`](scripts/create_github_repository_type.py) | Creates or updates the component type and its 14 properties (dry run unless `--apply`) |
| [`scripts/create_github_repository_scorecard.py`](scripts/create_github_repository_scorecard.py) | Creates the 2 filters, the scorecard and its 7 checks (dry run unless `--apply`) |
| [`terraform/`](terraform/) | Terraform / OpenTofu packages for the whole setup |
| [`github_actions/`](github_actions/) | Optional: a workflow that sets each repo's GitHub custom properties from a file in the repo, with CODEOWNERS review |

## Prerequisites

- An OpsLevel account with access to Custom Integrations, component types, filters and scorecards, and an
  OpsLevel API token with write access (for the scripts or Terraform).
- A team in OpsLevel to own the scorecard and checks.
- A GitHub organization, and permission to create a fine-grained personal access token for it and to define
  organization custom properties.
- Python 3.9+ for the scripts (standard library only).

---

## Suggested rollout plan

1. Create the GitHub token and custom properties (Part 1).
2. Create the component type and its relationship (Part 2).
3. Store the token as an OpsLevel secret and create the custom integration (Part 3).
4. Sync and validate the components (Part 4).
5. Create the filters and the scorecard (Part 5).
6. Link each repo component to the component it belongs to (Part 6).

---

## Part 1: GitHub side

### 1. Create a GitHub token

Create a **fine-grained personal access token**:

- Resource owner: your organization
- Repository access: **All repositories**
- Repository permissions: **Metadata: Read** (the default)

That covers private repositories and their custom property values; no organization permission is needed. A classic
token with the `repo` scope also works. If your org requires approval for fine-grained tokens, an org owner approves it.

### 2. Define the GitHub custom properties

In **GitHub → Organization settings → Custom properties**, define two properties (single select is recommended)
and set them on your repositories:

| Property | Values |
|---|---|
| `data_classification` | `public`, `internal`, `confidential`, `restricted` |
| `external_interface_type` | `none`, `internal_api`, `public_api`, `public_web` |

The org repos endpoint returns them under `custom_properties`. Repos without both set get no Risk Priority.

To manage the values as code instead of in the GitHub UI, see [`github_actions/`](github_actions/): each repo keeps
them in `.github/repo-properties.yml`, a security team reviews changes through CODEOWNERS, and a workflow writes
them to GitHub on merge.

---

## Part 2: Create the OpsLevel component type

### 3. Create the type and properties

```bash
cd scripts
export OPSLEVEL_API_TOKEN=...       # write access
# export OPSLEVEL_API_URL=https://<subdomain>.opslevel.com/graphql   # only if your account isn't on app.opslevel.com
python3 create_github_repository_type.py            # dry run: shows the plan
python3 create_github_repository_type.py --apply
```

The script creates the **GitHub Repository** type (alias `github_repository`) or, if it already exists, adds the
missing properties and updates the others (it never removes a property, and stops if the type has properties it
doesn't know). It checks the GraphQL input fields by introspection before changing anything. Every property is
set by the integration, so each is **locked in the UI** and **not allowed in `opslevel.yml`**.

| Property (alias) | Type | Source (GitHub field) |
|---|---|---|
| `name` (component name) | | `"GitHub Repo - " + .name` |
| `github_id` | integer | `.id` |
| `repository_name` | string | `.full_name` |
| `repository_description` | string | `.description` |
| `visibility` | string | `.visibility` |
| `archived` | boolean | `.archived` |
| `empty` | boolean | `.size == 0` |
| `creation_date` | date-time | `.created_at` |
| `updated_date` | date-time | `.pushed_at` (last push: the best "last had changes" signal) |
| `age_in_months` | integer | whole calendar months between `.created_at` and now |
| `top_languages` | string array | `[.language]` (primary language only) |
| `github_topics` | string array | `.topics` |
| `data_classification` | string | `.custom_properties.data_classification` |
| `external_interface_type` | string | `.custom_properties.external_interface_type` |
| `risk_priority` | `P1`–`P4` | computed, see [Risk Priority](#risk-priority) |

Component identifier (alias): `github_repo_<GitHub repo id>`. The id is unique and never changes, so a renamed
repository keeps its component, two repos whose names differ only in punctuation or case (`Order.Worker`,
`order_worker`) never share one, and the alias never collides with your service aliases.

You can also create the type in the UI (**Components → Manage Types → + New Component Type**, identifier
`github_repository`) and add the properties above with the same aliases.

### 4. Add the Component relationship

Nothing links a GitHub Repository component back to the Service, Backend, Frontend, etc. that the repository
belongs to: managed relationship rules match properties, aliases or contact details, not attached repositories.
Add a relationship to the type by hand: **Components → Manage Types → GitHub Repository → Relationships**, name
**Component**, alias `component`, allowed on the default category. You'll set it on each repo in Part 6.

---

## Part 3: Create the custom integration

### 5. Store the GitHub token as an OpsLevel secret

**Settings → Secrets → New Secret**, alias **`github_api_token`**, value: the token from step 1. The extractor
reads it with `{{ 'github_api_token' | secret }}`.

### 6. Create the custom integration

**Integrations → + New Integration → Custom Integration**. Name it, for example,
`Integration Data Mapping (Pull) - GitHub Repositories`.

### 7. Add the extractor YAML

Paste [`extract_definition.yaml`](extract_definition.yaml) and replace `<your_github_org>` with your org's login:

```yaml
---
extractors:
- external_kind: github_repos
  external_id: ".id | tostring"
  iterator: "."
  http_polling:
    method: GET
    url: '{% if cursor %}{{ cursor }}{% else %}https://api.github.com/orgs/<your_github_org>/repos?per_page=100&type=all{% endif %}'
    headers:
    - name: Authorization
      value: Bearer {{ 'github_api_token' | secret }}
    - name: Accept
      value: application/vnd.github+json
    - name: X-GitHub-Api-Version
      value: '2022-11-28'
    next_cursor:
      from: header
      value: '.link.next.target_url // null'
```

- `external_id` must be a string, hence `.id | tostring` (the GitHub id is a number).
- Paging: GitHub returns the next page's full URL in the `Link` response header (`rel="next"`). `next_cursor` reads
  it from the header, and the URL uses it when set, otherwise the first page. The last page has no `next` link,
  which ends the poll.

### 8. Add the transform YAML

Paste [`transform_definition.yaml`](transform_definition.yaml). The key parts:

```yaml
---
transforms:
- external_kind: github_repos
  opslevel_kind: github_repository
  opslevel_identifier: '"github_repo_\(.id)"'
  on_component_not_found: create
  properties:
    name: '"GitHub Repo - \(.name)"'
    github_id: .id
    repository_name: .full_name
    # ... see transform_definition.yaml for all 14 properties, including age_in_months and risk_priority
```

OpsLevel reformats a saved definition (sorted keys, double-quoted strings); that's expected.

#### Test the jq locally (optional)

[`example_github_api_response.json`](example_github_api_response.json) has the shape the org repos endpoint
returns. For example:

```bash
jq -c '.[] | {alias: "github_repo_\(.id)", name: "GitHub Repo - \(.name)", archived, dc: .custom_properties.data_classification}' example_github_api_response.json
```

With every property of the transform applied, the three sample repos come out as P1 (`payments-api`: confidential
data behind a public API), P3 (`Order.Worker`: internal data, internal API) and P4 (`legacy-site`: archived).

---

## Part 4: Sync and validate

### 9. Sync

Click **Sync** on the integration (it also polls on its own schedule). Then check:

- **Catalog** filtered to type **GitHub Repository**: one `GitHub Repo - <name>` component per repo.
- The integration's warnings: none expected. A warning naming a property usually means the property doesn't exist
  on the type (re-run the type script) or the value doesn't match its schema.

---

## Part 5: Scorecard

### Risk Priority

Computed in the transform on every sync from the two GitHub custom properties. Unset until both are set; archived
repositories are always P4.

| Data classification | Public interface (`public_api`, `public_web`) | `internal_api` / `none` |
|---|---|---|
| confidential / restricted | P1 | P2 |
| internal | P2 | P3 |
| public | P3 | P4 |

A **public** repository holding non-public data moves up one step (e.g. internal + internal_api = P3 → P2).
Property checks can't compare two properties, which is why the combination is computed into one `risk_priority`
value that the checks and the high-risk filter key off.

### 10. Create the filters, scorecard and checks

```bash
cd scripts
python3 create_github_repository_scorecard.py --owner <team_alias>            # dry run
python3 create_github_repository_scorecard.py --owner <team_alias> --apply    # [--disabled] [--affects-overall]
```

Re-running is safe: filters, the scorecard and its checks are matched by name and only missing ones are created.

| Filter | Matches |
|---|---|
| **GitHub Repositories (active)** | type GitHub Repository and `archived` isn't true (the scorecard's filter) |
| **GitHub Repositories - High risk (P1/P2)** | active and `risk_priority` is P1 or P2 (used by the high-risk checks) |

Scorecard **(Use Case) Security - GitHub Repository Risk**, all Custom Property checks with a jq predicate:

| Level | Check | Passes when |
|---|---|---|
| Bronze | Data classification is set | `data_classification` is public / internal / confidential / restricted |
| Bronze | External interface type is set | `external_interface_type` is none / internal_api / public_api / public_web |
| Silver | Repository has a description | `repository_description` isn't blank |
| Silver | Not a P1 risk | `risk_priority` != P1 |
| Gold | High risk: repository is not public | `visibility` != public (P1/P2 only) |
| Diamond* | High risk: pushed to in the last 90 days | `updated_date` within 90 days (P1/P2 only) |
| Diamond* | Risk priority P3 or lower | `risk_priority` is P3 or P4 |

\* On the highest level your rubric has if it has no Diamond level. Checks limited to P1/P2 don't apply to
lower-risk repos, so those aren't held back by them.

---

## Part 6: Link repos to their components

### 11. Set the Component relationship

On each GitHub Repository component, set **Component** to the Service, Backend, Frontend, etc. the repository
belongs to, so owners can find their repositories and scores. This is manual and goes stale when repos move; see
[Extending](#extending-the-integration) for ways to automate it.

---

## Troubleshooting

#### The poll returns 401

The token is expired, revoked or missing. Create a new one (step 1) and update the `github_api_token` secret.

#### No components are created

Check:

- the extractor's `external_kind` (`github_repos`) matches the transform's `external_kind`
- the component type alias is `github_repository` (the transform's `opslevel_kind`)
- `<your_github_org>` was replaced in the extractor URL
- `external_id` is `.id | tostring`, not `.id`

#### Only some repositories appear

Each page of 100 repositories is a separate request. Check that the extractor still has the `next_cursor` block
(without it, only the first page is read) and that the token is valid.

#### Private repositories are missing

The token can't see them: check it has **All repositories** access with your org as resource owner, and that the
org has approved it if approval is required.

#### `data_classification` / `risk_priority` are empty

The repo doesn't have both GitHub custom properties set, or the token can't read them (Metadata: Read is enough).

#### The scorecard script stops with "lacks properties"

Run `create_github_repository_type.py --apply` first.

---

## Limits

- **Primary language only.** `top_languages` holds `.language`; the full list needs `/repos/{repo}/languages` per repo.
- **No automatic link** between a repo component and the component it belongs to (see Part 6).

## Extending the integration

- **More properties from the same payload.** The transform receives the full repo object, so properties such as
  `default_branch: .default_branch` or `has_issues: .has_issues` only need a property on the type and a line in the
  transform. Add them to `PROPERTIES` in the type script too.
- **Properties the org endpoint doesn't return** (CodeQL status, branch rulesets, top contributors) need per-repo
  API calls or a separate integration; add them with their own source, then add checks for them (for example, CodeQL
  enabled on P1/P2 repos).
- **Automatic repo → component link.** Two options: (1) a GitHub custom property such as `opslevel_service` mapped to
  a property and matched by a managed relationship rule; (2) a second extractor polling OpsLevel's GraphQL API for
  each component's attached repositories, writing the owning component's alias onto the repo component, plus an
  "array contains" managed relationship rule.
- **Metadata on Services instead of new components.** See the
  [`github_service_properties`](terraform/github_service_properties/) Terraform package.
