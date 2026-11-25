# GitHub Repositories → OpsLevel: step-by-step setup

Manual setup of the GitHub Repositories custom integration described in the [README](README.md): the component type
and scorecard are created by two Python scripts, the integration is pasted in the OpsLevel UI, and the risk tags are
set by hand. To create everything from code instead, use the [Terraform packages](terraform/).

## Prerequisites

- An OpsLevel account with access to Custom Integrations, component types, filters and scorecards, and an
  OpsLevel API token with write access (for the scripts or Terraform).
- A team in OpsLevel to own the scorecard and checks.
- A GitHub organization, and permission to create a fine-grained personal access token for it.
- Python 3.9+ for the scripts (standard library only).

---

## Suggested rollout plan

1. Create the GitHub token (Part 1).
2. Create the component type and its relationship (Part 2).
3. Store the token as an OpsLevel secret and create the custom integration (Part 3).
4. Sync and validate the components (Part 4).
5. Classify the repositories with tags (Part 5).
6. Create the filters and the scorecard (Part 6).
7. Link each repo component to the component it belongs to (Part 7).

---

## Part 1: GitHub side

### 1. Create a GitHub token

Create a **fine-grained personal access token**:

- Resource owner: your organization
- Repository access: **All repositories**
- Repository permissions: **Metadata: Read** (the default)

That covers private repositories; no organization permission is needed. A classic token with the `repo` scope also
works. If your org requires approval for fine-grained tokens, an org owner approves it.

---

## Part 2: Create the OpsLevel component type

### 2. Create the type and properties

```bash
cd scripts
export OPSLEVEL_API_TOKEN=...       # write access
# export OPSLEVEL_API_URL=https://<subdomain>.opslevel.com/graphql   # only if your account isn't on app.opslevel.com
python3 create_github_repository_type.py            # dry run: shows the plan
python3 create_github_repository_type.py --apply
```

The script creates the **GitHub Repository** type (alias `github_repository`) or, if it already exists, adds the
missing properties and updates the others. It never removes a property: if the type has properties the script
doesn't know, the dry run lists them and `--apply` stops until they're added to `PROPERTIES`. It checks the GraphQL
input fields by introspection before changing anything. Every property is set by the integration, so each is
**locked in the UI** and **not allowed in `opslevel.yml`**.

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

Component identifier (alias): `github_repo_<GitHub repo id>`. The id is unique and never changes, so a renamed
repository keeps its component, two repos whose names differ only in punctuation or case (`Order.Worker`,
`order_worker`) never share one, and the alias never collides with your service aliases. OpsLevel also gives each
component an alias derived from its name (`GitHub Repo - payments-api` → `github_repo_-_payments-api`).

You can also create the type in the UI (**Components → Manage Types → + New Component Type**, identifier
`github_repository`) and add the properties above with the same aliases.

### 3. Add the Component relationship

Nothing links a GitHub Repository component back to the Service, Backend, Frontend, etc. that the repository
belongs to: managed relationship rules match properties, aliases or contact details, not attached repositories.
Add a relationship to the type by hand: **Components → Manage Types → GitHub Repository → Relationships**, name
**Component**, alias `component`, allowed on the default category. You'll set it on each repo in Part 7.

---

## Part 3: Create the custom integration

### 4. Store the GitHub token as an OpsLevel secret

**Settings → Secrets → New Secret**, alias **`github_api_token`**, value: the token from step 1. The extractor
reads it with `{{ 'github_api_token' | secret }}`.

### 5. Create the custom integration

**Integrations → + New Integration → Custom Integration**. Name it, for example,
`Integration Data Mapping (Pull) - GitHub Repositories`.

### 6. Add the extractor YAML

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

### 7. Add the transform YAML

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
    # ... see transform_definition.yaml for all 11 properties, including age_in_months
```

OpsLevel reformats a saved definition (sorted keys, double-quoted strings); that's expected.

#### Test the jq locally (optional)

[`example_github_api_response.json`](example_github_api_response.json) has the shape the org repos endpoint
returns. For example:

```bash
jq -c '.[] | {alias: "github_repo_\(.id)", name: "GitHub Repo - \(.name)", archived, empty: (.size == 0)}' example_github_api_response.json
```

---

## Part 4: Sync and validate

### 8. Sync

Click **Sync** on the integration (it also polls on its own schedule). Then check:

- **Catalog** filtered to type **GitHub Repository**: one `GitHub Repo - <name>` component per repo.
- The integration's warnings: none expected. A warning naming a property usually means the property doesn't exist
  on the type (re-run the type script) or the value doesn't match its schema.

---

## Part 5: Classify repositories

### Risk tags

Each GitHub Repository component gets three tags. They aren't synced from GitHub: someone who knows what the repo
holds sets them (security, or the owning team with security's review).

| Tag | Values |
|---|---|
| `data_classification` | `public`, `internal`, `confidential`, `restricted` |
| `external_interface_type` | `none` (library, batch job, docs), `internal_api` (only internal callers), `public_api` (reachable from outside), `public_web` (a site or app end users open) |
| `risk_priority` | `P1`–`P4` |

### Risk Priority

Suggested default for `risk_priority` (impact × exposure; a starting point to adjust, not from a published standard):

| Data classification | Public interface (`public_api`, `public_web`) | `internal_api` / `none` |
|---|---|---|
| confidential / restricted | P1 | P2 |
| internal | P2 | P3 |
| public | P3 | P4 |

Set a different value where you know better (for example, an internal batch job that handles payment files).

### 9. Set the tags

- **By hand:** on each GitHub Repository component, **Tags → Add tag** with the three keys and values.
- **As code:** the [Terraform component package](terraform/github_repository_component/) takes a
  `repo_classifications` map keyed by repo name and tags every component, deriving `risk_priority` from the table
  above when you leave it out. Its tags attach to the name-derived alias (`github_repo_-_<repo>`), so run it after
  the first sync.

Tags live on the OpsLevel component, so they survive syncs, and a renamed repo keeps them (its component keeps the
same `github_repo_<id>` identifier).

---

## Part 6: Scorecard

### 10. Create the filters, scorecard and checks

```bash
cd scripts
python3 create_github_repository_scorecard.py --owner <team_alias>            # dry run
python3 create_github_repository_scorecard.py --owner <team_alias> --apply    # [--disabled] [--affects-overall true|false]
```

Re-running is safe: filters, the scorecard and its checks are matched by name and only missing ones are created.
`--affects-overall` sets whether the scorecard affects overall levels (off for a new scorecard; left as is on a
re-run unless you pass it).

| Filter | Matches |
|---|---|
| **GitHub Repositories (active)** | type GitHub Repository and `archived` isn't true (the scorecard's filter) |
| **GitHub Repositories - risk_priority P1 or P2** | `risk_priority` tag is P1 **or** P2 (a filter has one connective, so the OR is its own filter) |
| **GitHub Repositories - High risk (P1/P2)** | both of the above (used by the high-risk checks) |

Scorecard **(Use Case) Security - GitHub Repository Risk**: four Tag Defined checks on the risk tags and three
Custom Property checks on the synced metadata.

| Level | Check | Passes when |
|---|---|---|
| Bronze | Data classification tag is set | `data_classification` tag is public / internal / confidential / restricted |
| Bronze | External interface type tag is set | `external_interface_type` tag is none / internal_api / public_api / public_web |
| Silver | Repository has a description | `repository_description` property isn't blank |
| Silver | Not a P1 risk | `risk_priority` tag isn't P1 |
| Gold | High risk: repository is not public | `visibility` property isn't public (P1/P2 only) |
| Diamond* | High risk: pushed to in the last 90 days | `updated_date` property within 90 days (P1/P2 only) |
| Diamond* | Risk priority P3 or lower | `risk_priority` tag is P3 or P4 |

\* On the highest level your rubric has if it has no Diamond level. Checks limited to P1/P2 don't apply to
lower-risk repos, so those aren't held back by them. A Tag Defined check fails when the tag is missing, so
unclassified repos stay at Beginner.

---

## Part 7: Link repos to their components

### 11. Set the Component relationship

On each GitHub Repository component, set **Component** to the Service, Backend, Frontend, etc. the repository
belongs to, so owners can find their repositories and scores. This is manual and goes stale when repos move; see
[Extending](README.md#extending-the-integration) for ways to automate it.

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

#### Every repo fails the Bronze checks

No repo has its risk tags yet (Part 5). Tag keys must be exactly `data_classification` and
`external_interface_type`, with values from the tables above.

#### The scorecard script stops with "lacks properties"

Run `create_github_repository_type.py --apply` first.
