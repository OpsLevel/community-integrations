# OpsLevel package: GitHub Repository component

Catalogs every repository in a GitHub organization as a **GitHub Repository** component and grades it on
risk-based standards. OpsLevel doesn't run maturity checks on the repository object itself, so a component per
repository makes that possible.

This is the Terraform version of the [step-by-step guide](../../step_by_step_setup.md): same component type,
integration, risk tags, filters and scorecard.

## What it creates

| Resource | Details |
|---|---|
| Component type **GitHub Repository** (`github_repository`) | 10 properties synced from GitHub (below) and a **Component** relationship you set by hand to the Service, Backend, Frontend, etc. the repository belongs to |
| Custom integration **Integration Data Mapping (Pull) - GitHub Repositories** | Polls `GET /orgs/<org>/repos` and creates or updates one component per repository, named `GitHub Repo - <name>`, identified by the GitHub repo id (alias `github_repo_<id>`), so renamed or similarly named repos never share a component |
| Secret `github_api_token` | The GitHub token the integration uses (`manage_secrets = false` to reuse an existing one) |
| Risk tags | `data_classification`, `external_interface_type` and `risk_priority` on each GitHub Repository component, from `repo_classifications` |
| Filters | **GitHub Repositories (active)** (not archived), **GitHub Repositories - risk_priority P1 or P2** (tag) and **GitHub Repositories - High risk (P1/P2)** (both) |
| Scorecard **(Use Case) Security - GitHub Repository Risk** | 7 checks: 4 Tag Defined checks on the risk tags, 3 Custom Property checks ([main guide](../../step_by_step_setup.md#part-6-scorecard)) |

Properties (all set by the integration, locked in the UI): GitHub ID, Repository Name, Repository Description,
Visibility, archived, empty, Creation Date, Updated Date (last push), Age (in months), GitHub Topics.

## After apply

The risk tags go on components the integration creates, so on a new account: `apply`, click **Sync** on the
integration, then `apply` again to add the tags.

Set each repository's **Component** relationship to the component it belongs to, so owners can find their
repositories and their scores. OpsLevel can't link them automatically today.

## Choosing between the two packages

See [../README.md](../README.md#choosing-a-package).

## Risk tags

Each repository in `repo_classifications` gets three tags on its GitHub Repository component:

| Tag | Values |
|---|---|
| `data_classification` | public, internal, confidential, restricted |
| `external_interface_type` | none (library, batch job, docs), internal_api (only internal callers), public_api (reachable from outside), public_web (a site or app end users open) |
| `risk_priority` | P1–P4; set it per repository, or leave it out to use the suggested default below |

Suggested default for `risk_priority` (impact × exposure; a starting point to adjust, not from a published standard):

| Data classification | Public interface (`public_api`, `public_web`) | `internal_api` / `none` |
|---|---|---|
| confidential / restricted | P1 | P2 |
| internal | P2 | P3 |
| public | P3 | P4 |

```hcl
repo_classifications = {
  "payments-api" = { data_classification = "restricted", external_interface_type = "public_api" }   # P1
  "docs-site"    = { data_classification = "public", external_interface_type = "public_web" }       # P3
  "legacy-batch" = { data_classification = "internal", external_interface_type = "none", risk_priority = "P2" }
}
```

Keys are GitHub repository names. The tags are attached by the alias OpsLevel derives from the component name
(`GitHub Repo - payments-api` → `github_repo_-_payments-api`). For repo names with characters other than letters,
digits, `-` and `_`, check the component's aliases in OpsLevel after the first sync: if the derived alias differs,
`apply` fails for that repo with a "not found" error.

## Scorecard checks

Same 7 checks as the step-by-step guide: see [Scorecard](../../step_by_step_setup.md#part-6-scorecard).
Checks written for Diamond go on Gold when `rubric_level_count = 3` (the default).

## Prerequisites

- Terraform or OpenTofu ≥ 1.5 and the OpsLevel provider ≥ 1.14.
- An OpsLevel API token with write access (`OPSLEVEL_API_TOKEN`), a team to own the scorecard, and a rubric with
  at least 3 levels above Beginner.
- A GitHub fine-grained token: your org as resource owner, all repositories, Repository permission
  **Metadata: Read** (covers private repos; no organization permission needed).

## Deploy

```bash
cd example
cp terraform.tfvars.example terraform.tfvars   # GitHub org, owner team, GitHub token
export OPSLEVEL_API_TOKEN=...
terraform init && terraform plan && terraform apply
```

Then open the new integration in OpsLevel and click **Sync** (it also polls on its own schedule).

## Limits

- Reads every repository in the org, 100 per request, following GitHub's `Link` header to the next page.
- Not created: properties nothing syncs from GitHub (CodeQL status, branch rules, contributors); add them with
  their own source when something populates them.
- Classification is kept in Terraform, not GitHub, so it can drift from reality unless someone owns updating it.

## Potential additions: classification from GitHub custom properties

Instead of tags set in Terraform, the classification can live in GitHub and be synced like the other metadata.
This needs configuring custom properties in GitHub first:

1. In the GitHub org settings, create the custom properties `data_classification` and `external_interface_type`
   (single select, values above) and set them on each repository (by hand, through the API, or from a file in each
   repo with a workflow; tick **Allow repository actors to set this property** for the workflow route).
2. Add properties for them (and a computed `risk_priority`) to the component type, and map them in the transform:
   `data_classification: .custom_properties.data_classification // null`, likewise for
   `external_interface_type`. The org repos endpoint already returns `custom_properties`; the token's
   Metadata: Read permission is enough to read them.
3. Point the Bronze checks and the P1/P2 filter at the properties instead of the tags, and drop
   `repo_classifications`.
