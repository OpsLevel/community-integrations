# Option A: GitHub Repository component

Catalogs every repository in a GitHub organization as a **GitHub Repository** component, kept up to date by a pull
custom integration. OpsLevel doesn't run maturity checks on the repository object itself, so a component per
repository is what makes repository-level checks possible.

## What it creates

| Resource | Details |
|---|---|
| Component type **GitHub Repository** (`github_repository`) | 10 properties synced from GitHub (below) and a **Component** relationship you set by hand to the Service, Backend, Frontend, etc. the repository belongs to |
| Custom integration **Integration Data Mapping (Pull) - GitHub Repositories** | Polls `GET /orgs/<org>/repos` and creates or updates one component per repository, named `GitHub Repo - <name>`, identified by the GitHub repo id (alias `github_repo_<id>`), so renamed or similarly named repos never share a component |
| Secret `github_api_token` | The GitHub token the integration uses (`manage_secrets = false` to reuse an existing one) |

## Properties

All set by the integration: locked in the UI and not allowed in `opslevel.yml`.

| Property (alias) | Type | Source (GitHub field) |
|---|---|---|
| `github_id` | integer | `.id` |
| `repository_name` | string | `.full_name` |
| `repository_description` | string | `.description` |
| `visibility` | string | `.visibility` |
| `archived` | boolean | `.archived` |
| `empty` | boolean | `.size == 0` |
| `creation_date` | date-time | `.created_at` |
| `updated_date` | date-time | `.pushed_at` (last push: the best "last had changes" signal) |
| `age_in_months` | integer | whole calendar months between `.created_at` and now |
| `github_topics` | string array | `.topics` |

The extract and transform definitions are in [`modules/github_repository/definitions/`](modules/github_repository/definitions/).

## Deploy

```bash
cd example
cp terraform.tfvars.example terraform.tfvars   # GitHub org, owner team, GitHub token
export OPSLEVEL_API_TOKEN=...
terraform init && terraform plan && terraform apply
```

Then open the new integration in OpsLevel and click **Sync** (it also polls on its own schedule).

## After the first sync

Set each repository's **Component** relationship to the component it belongs to, so owners can find their
repositories. OpsLevel can't link them automatically today.

To grade the repositories, add the [risk scorecard](../risk_scorecard/).
