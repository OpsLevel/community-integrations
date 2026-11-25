# GitHub Repositories → OpsLevel Custom Integration (Terraform)

Two Terraform (or OpenTofu) packages that pull every repository in a GitHub organization into OpsLevel through a
**pull** custom integration, classify each repo's risk with OpsLevel tags, and grade the repos on a risk-based
scorecard. OpsLevel doesn't run maturity checks on the repository object itself, so the repository has to become (or
be attached to) a component for repository-level checks to work.

| Package | What it does |
|---|---|
| [`github_repository_component/`](github_repository_component/) (recommended) | One **GitHub Repository** component per repo, with repo metadata as properties. |
| [`github_service_properties/`](github_service_properties/) | The same metadata as `github_*` custom properties on your existing **Services**. No new components. |

## Overview

```text
GitHub REST API: GET /orgs/<org>/repos   (polled by OpsLevel on a schedule, every page)
  ↓
OpsLevel Custom Integration (pull), created by Terraform
  ↓
Extract + transform definitions (modules/*/definitions/)
  ↓
"GitHub Repository" components (or properties on Services)  +  risk tags from your tfvars
  ↓
Filters + "(Use Case) Security - GitHub Repository Risk" scorecard
```

Nothing runs on your infrastructure: OpsLevel calls the GitHub API with a token stored as an OpsLevel secret.

## What you get

Each package creates:

- **The integration** and the **`github_api_token` secret** it reads. It follows GitHub's `Link` header, so every
  repo in the org is read, 100 per request. Repo components are identified by the GitHub repo id
  (`github_repo_<id>`), so renamed repos keep their component.
- **10 properties** synced from GitHub: name, description, visibility, archived, empty, creation and last-push dates,
  age in months, topics.
- **Risk tags** on each repo component (or Service): `data_classification`, `external_interface_type` and
  `risk_priority` (P1–P4), from a map in your tfvars. `risk_priority` defaults to a suggested impact × exposure matrix
  when you leave it out.
- **Filters and a scorecard**: 7 checks from "classified" (Bronze) to "low risk and actively maintained" (Diamond),
  with the strictest controls applying only to P1/P2 repos.

Each package's README has the full property list, the risk matrix and the checks.

## Choosing a package

| | **GitHub Repository component** | **GitHub properties on Service** |
|---|---|---|
| Where the data lives | A new component type, one component per repository (`GitHub Repo - <name>`) | Custom properties on your existing Services |
| Risk classification | Tags on each repo component, from `repo_classifications` | Tags on each Service, from `service_classifications` |
| Repos without a service | Cataloged and graded | Skipped |
| Services with several repos / monorepos | Each repo graded on its own | One repo's metadata per service (the last one synced wins); risk tags are set per service |
| Linking repo ↔ service | Manual **Component** relationship on each repo component | Automatic by name, or the repo's `opslevel_service` GitHub custom property |
| Who sees the scorecard | Repo components (owned through the Component link) | The owning team, on the service they already own |
| Catalog growth | One component per repository | None |

Pick one. Both create a secret with the same alias (`github_api_token`), so to switch, `terraform destroy` the first
one before applying the other (or give one of them a different `github_token_secret_alias`).

## Prerequisites

- Terraform or OpenTofu ≥ 1.5 and the OpsLevel provider ≥ 1.14.
- An OpsLevel API token with write access, a team to own the scorecard (`owner_team_alias`), and rubric levels with
  index 1–3 (set `rubric_level_count = 4` if your rubric also has a Diamond level).
- A GitHub **fine-grained personal access token**: your org as resource owner, **All repositories**, Repository
  permission **Metadata: Read** (the default). That covers private repositories; no organization permission is
  needed. A classic token with the `repo` scope also works. If your org requires approval for fine-grained tokens,
  an org owner approves it.

## Deploy

```bash
cd github_repository_component/example      # or github_service_properties/example
cp terraform.tfvars.example terraform.tfvars  # GitHub org, owner team alias, GitHub token, classifications
export OPSLEVEL_API_TOKEN=...                 # OpsLevel API token with write access
# export OPSLEVEL_API_URL=https://<subdomain>.opslevel.com   # only if your account isn't on app.opslevel.com
terraform init && terraform plan && terraform apply
```

Then open the new custom integration in OpsLevel and click **Sync** (it also polls on its own schedule).

- **Component package on a new account:** the risk tags go on components the first sync creates, so `apply` (leave
  `repo_classifications` empty or expect tag errors), **Sync**, then `apply` again to add the tags.
- **Existing secret:** if `github_api_token` already exists in your account, set `manage_secrets = false`.
- `terraform.tfvars` holds your GitHub token: keep it out of version control (each package's `.gitignore` already
  excludes it).

To reclassify a repo later, edit its entry in the classifications map and `apply`.

## Troubleshooting

#### The poll returns 401

The token is expired, revoked or missing. Create a new one and update the `github_api_token` secret (or set
`github_token` and `apply`).

#### Private repositories are missing

The token can't see them: check it has **All repositories** access with your org as resource owner, and that the
org has approved it if approval is required.

#### `apply` fails with "not found" on a risk tag

The component doesn't exist yet (run **Sync** first), or the repo name derives a different alias than
`github_repo_-_<repo>` (see the component package README).

#### Every repo fails the Bronze checks

The repo has no risk tags yet: add it to `repo_classifications` / `service_classifications` and `apply`.

## Known issues

- OpsLevel provider v1.14.x fails to create a component type property whose `description` is `""` ("Provider
  produced inconsistent result after apply"). Every property in these packages has a description; keep it that way
  if you add more.
- `opslevel_component_type` doesn't expose property definition ids, so the component package's filters reference
  properties by alias in `key_data` (the API accepts it; confirmed working). The Services package uses the property
  definition id.
- `opslevel_service_tag` needs a component alias. The component package uses the alias OpsLevel derives from the
  component name (`github_repo_-_<repo>`), not the integration's `github_repo_<id>` identifier, because Terraform
  doesn't know GitHub repo ids.
- `opslevel_property_definition` has no `alias` argument and always targets the default component type, so the
  Services package assumes the alias OpsLevel derives from each property name (see its README).

## Limits

- **Classification is kept in Terraform, not GitHub,** so it can drift from reality unless someone owns updating it.
- **No automatic link** between a repo component and the component it belongs to: set the **Component**
  relationship on each repo component by hand.

## Potential additions

### Classification from GitHub custom properties

Instead of tags set in Terraform, the classification can live in GitHub and be synced like the other metadata. This
needs configuring custom properties in GitHub first:

1. In **GitHub → Organization settings → Custom properties**, create `data_classification` and
   `external_interface_type` (single select) and set them on each repository: by hand, through the API, or from a
   file in each repo with a workflow (tick **Allow repository actors to set this property** for the workflow route).
2. Add properties for them to the component type, and map them in the transform:
   `data_classification: .custom_properties.data_classification // null`, likewise for
   `external_interface_type`. Compute `risk_priority` in the transform with jq from the two values. The org repos
   endpoint already returns `custom_properties`; the token's Metadata: Read permission is enough to read them.
3. Point the Bronze checks and the P1/P2 filter at the properties instead of the tags, and drop the classifications
   map.

### Extending the integration

- **More properties from the same payload.** The transform receives the full repo object, so properties such as
  `default_branch: .default_branch` or `has_issues: .has_issues` only need a property on the type and a line in the
  transform (`modules/*/definitions/`).
- **Languages.** The org repos endpoint only returns the primary `.language`; a full list per repo needs a chained
  extractor that calls `/repos/{owner}/{repo}/languages` for each repo, plus an array property on the type.
- **Properties the org endpoint doesn't return** (CodeQL status, branch rulesets, top contributors) need per-repo
  API calls or a separate integration; add them with their own source, then add checks for them (for example, CodeQL
  enabled on P1/P2 repos).
- **Automatic repo → component link.** Two options: (1) a GitHub custom property such as `opslevel_service` mapped to
  a property and matched by a managed relationship rule; (2) a second extractor polling OpsLevel's GraphQL API for
  each component's attached repositories, writing the owning component's alias onto the repo component, plus an
  "array contains" managed relationship rule.
