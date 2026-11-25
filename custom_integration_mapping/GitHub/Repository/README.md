# GitHub Repositories → OpsLevel Custom Integration (Terraform)

A **pull** custom integration that reads every repository in a GitHub organization and brings its metadata into
OpsLevel: description, visibility, archived, empty, creation and last-push dates, age, topics. Two Terraform (or
OpenTofu) packages set it up, depending on where you want the data to land.

| Option | What it does |
|---|---|
| **A. [GitHub Repository component](github_repository_component/)** (recommended) | One **GitHub Repository** component per repo, with the metadata as properties. |
| **B. [GitHub properties on Service](github_service_properties/)** | The same metadata as `github_*` custom properties on your existing **Services**. No new components. |

**Extended usage:** [`risk_scorecard/`](risk_scorecard/) builds on either option to classify repos by risk with
OpsLevel tags and grade them on a risk-based scorecard.

## Overview

```text
GitHub REST API: GET /orgs/<org>/repos   (polled by OpsLevel on a schedule, every page)
  ↓
OpsLevel Custom Integration (pull), created by Terraform
  ↓
Extract + transform definitions (modules/*/definitions/)
  ↓
A: "GitHub Repository" components (one per repo)   or   B: github_* properties on matching Services
```

Nothing runs on your infrastructure: OpsLevel calls the GitHub API with a token stored as an OpsLevel secret. The
extractor follows GitHub's `Link` header, so every repo in the org is read, 100 per request.

## Choosing an option

| | **A. GitHub Repository component** | **B. GitHub properties on Service** |
|---|---|---|
| Where the data lives | A new component type, one component per repository (`GitHub Repo - <name>`) | Custom properties on your existing Services |
| Repos without a service | Cataloged | Skipped |
| Services with several repos / monorepos | Each repo is its own component | One repo's metadata per service (the last one synced wins) |
| Linking repo ↔ service | Manual **Component** relationship on each repo component | Automatic by name, or the repo's `opslevel_service` GitHub custom property |
| Who sees the data | Repo components (owned through the Component link) | The owning team, on the service they already own |
| Catalog growth | One component per repository | None |

Pick one. Both create a secret with the same alias (`github_api_token`), so to switch, `terraform destroy` the first
one before applying the other (or give one of them a different `github_token_secret_alias`).

## Prerequisites

- Terraform or OpenTofu ≥ 1.5 and the OpsLevel provider ≥ 1.14.
- An OpsLevel API token with write access, and a team to own the secret (`owner_team_alias`).
- A GitHub **fine-grained personal access token**: your org as resource owner, **All repositories**, Repository
  permission **Metadata: Read** (the default). That covers private repositories; no organization permission is
  needed. A classic token with the `repo` scope also works. If your org requires approval for fine-grained tokens,
  an org owner approves it.

## Deploy

```bash
cd github_repository_component/example      # or github_service_properties/example
cp terraform.tfvars.example terraform.tfvars  # GitHub org, owner team alias, GitHub token
export OPSLEVEL_API_TOKEN=...                 # OpsLevel API token with write access
# export OPSLEVEL_API_URL=https://<subdomain>.opslevel.com   # only if your account isn't on app.opslevel.com
terraform init && terraform plan && terraform apply
```

Then open the new custom integration in OpsLevel and click **Sync** (it also polls on its own schedule).

- **Existing secret:** if `github_api_token` already exists in your account, set `manage_secrets = false`.
- `terraform.tfvars` holds your GitHub token: keep it out of version control (each package's `.gitignore` already
  excludes it).

## Troubleshooting

#### The poll returns 401

The token is expired, revoked or missing. Create a new one and update the `github_api_token` secret (or set
`github_token` and `apply`).

#### Private repositories are missing

The token can't see them: check it has **All repositories** access with your org as resource owner, and that the
org has approved it if approval is required.

#### Option B: some repositories don't show up on a Service

The repo name didn't match a Service alias (they show as warnings on the integration). See
[how a repository is matched](github_service_properties/README.md#how-a-repository-is-matched-to-a-service).

## Known issues

- OpsLevel provider v1.14.x fails to create a component type property whose `description` is `""` ("Provider
  produced inconsistent result after apply"). Every property in these packages has a description; keep it that way
  if you add more.
- `opslevel_property_definition` has no `alias` argument and always targets the default component type, so option B
  assumes the alias OpsLevel derives from each property name (see its README).

## Limits

- **No automatic link** between a repo component (option A) and the component it belongs to: set the **Component**
  relationship on each repo component by hand.

## Extending the integration

- **Risk classification and a scorecard.** See [`risk_scorecard/`](risk_scorecard/).
- **More properties from the same payload.** The transform receives the full repo object, so properties such as
  `default_branch: .default_branch` or `has_issues: .has_issues` only need a property on the type and a line in the
  transform (`modules/*/definitions/`).
- **Languages.** The org repos endpoint only returns the primary `.language`; a full list per repo needs a chained
  extractor that calls `/repos/{owner}/{repo}/languages` for each repo, plus an array property on the type.
- **Properties the org endpoint doesn't return** (CodeQL status, branch rulesets, top contributors) need per-repo
  API calls or a separate integration.
- **Automatic repo → component link.** Two options: (1) a GitHub custom property such as `opslevel_service` mapped to
  a property and matched by a managed relationship rule; (2) a second extractor polling OpsLevel's GraphQL API for
  each component's attached repositories, writing the owning component's alias onto the repo component, plus an
  "array contains" managed relationship rule.
