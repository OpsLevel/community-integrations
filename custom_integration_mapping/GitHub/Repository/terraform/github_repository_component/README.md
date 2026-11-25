# OpsLevel package: GitHub Repository component

Catalogs every repository in a GitHub organization as a **GitHub Repository** component and grades it on
risk-based standards. OpsLevel doesn't run maturity checks on the repository object itself, so a component per
repository makes that possible.

This is the Terraform version of the step-by-step guide in [../../README.md](../../README.md): same component type,
integration, filters and scorecard.

## What it creates

| Resource | Details |
|---|---|
| Component type **GitHub Repository** (`github_repository`) | 14 properties synced from GitHub (below) and a **Component** relationship you set by hand to the Service, Backend, Frontend, etc. the repository belongs to |
| Custom integration **Integration Data Mapping (Pull) - GitHub Repositories** | Polls `GET /orgs/<org>/repos` and creates or updates one component per repository, named `GitHub Repo - <name>` |
| Secret `github_api_token` | The GitHub token the integration uses (`manage_secrets = false` to reuse an existing one) |
| Filters | **GitHub Repositories (active)** (not archived) and **GitHub Repositories - High risk (P1/P2)** |
| Scorecard **(Use Case) Security - GitHub Repository Risk** | 7 Custom Property checks ([main guide](../../README.md#part-5-scorecard)) |

Properties (all set by the integration, locked in the UI): GitHub ID, Repository Name, Repository Description,
Visibility, archived, empty, Creation Date, Updated Date (last push), Age (in months), Top Languages, GitHub Topics,
Data Classification, External Interface Type, Risk Priority.

## After apply

Set each repository's **Component** relationship to the component it belongs to, so owners can find their
repositories and their scores. OpsLevel can't link them automatically today.

## Choosing between the two packages

See [../README.md](../README.md#choosing-a-package).

## Risk Priority and scorecard checks

The risk matrix and the 7 checks are the same in both packages; see
[Risk Priority](../../README.md#risk-priority) and [Scorecard](../../README.md#part-5-scorecard) in the main guide.
Checks written for Diamond go on Gold when `rubric_level_count = 3` (the default).

## Prerequisites

- Terraform or OpenTofu ≥ 1.5 and the OpsLevel provider ≥ 1.14.
- An OpsLevel API token with write access (`OPSLEVEL_API_TOKEN`), a team to own the scorecard, and a rubric with
  at least 3 levels above Beginner.
- A GitHub fine-grained token: your org as resource owner, all repositories, Repository permission
  **Metadata: Read** (covers private repos and custom property values; no organization permission needed).
- The `data_classification` and `external_interface_type` custom properties defined in your GitHub org.

## Deploy

```bash
cd example
cp terraform.tfvars.example terraform.tfvars   # GitHub org, owner team, GitHub token
export OPSLEVEL_API_TOKEN=...
terraform init && terraform plan && terraform apply
```

Then open the new integration in OpsLevel and click **Sync** (it also polls on its own schedule).

## Limits

- Reads the first 100 repositories of the org (one page); larger orgs need paging added to the extractor.
- `Languages` holds the primary language only.
- Not created: properties nothing syncs from GitHub (CodeQL status, branch rules, contributors); add them with
  their own source when something populates them.
