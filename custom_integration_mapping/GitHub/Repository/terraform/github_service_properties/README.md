# OpsLevel package: GitHub properties on Service

Adds GitHub repository metadata to your existing **Services** as custom properties and grades the services on
risk-based standards. No new component type: owners see the data and the scorecard on the services they already own.

> **Status:** less tested than the [GitHub Repository component](../github_repository_component/) package, which has
> been applied end to end. The derived property aliases (below) haven't been confirmed against a live account, so
> run `terraform plan` and check the `expected_property_aliases` output after the first apply.

## What it creates

| Resource | Details |
|---|---|
| 11 custom properties on the default component type (Service), prefixed `github_` | Set by the integration, locked in the UI (below) |
| Custom integration **Integration Data Mapping (Pull) - GitHub Repo Metadata on Services** | Polls `GET /orgs/<org>/repos` and writes each repository's metadata onto its Service. Creates nothing; repositories with no matching Service are skipped |
| Secret `github_api_token` | The GitHub token the integration uses (`manage_secrets = false` to reuse an existing one) |
| Risk tags | `data_classification`, `external_interface_type` and `risk_priority` on each Service in `service_classifications` |
| Filters | **Services with a GitHub repo (active)**, **Services - risk_priority P1 or P2** (tag) and **Services with a GitHub repo - High risk (P1/P2)** (both) |
| Scorecard **(Use Case) Security - Service GitHub Repository Risk** | 7 checks: 4 Tag Defined checks on the risk tags, 3 Custom Property checks ([main guide](../../step_by_step_setup.md#part-6-scorecard)) |

Properties: GitHub Repo ID, Full Name, Description, Visibility, Archived, Empty, Created At, Last Pushed At,
Age In Months, Languages, Topics.

## How a repository is matched to a Service

1. Optional: the repository's `opslevel_service` GitHub custom property, if your org defines it: the Service's alias.
2. Otherwise the repository name, lowercased, with `-` turned into `_` (`shopping-cart-service` →
   `shopping_cart_service`).

Repositories that match no Service are skipped (they show as warnings on the integration). Set `opslevel_service`
on repositories whose name doesn't match. One repository maps to one Service; a monorepo's metadata goes to one
service only.

**Several repositories on one Service:** the integration writes each repository in turn, so the Service keeps the
metadata (visibility, last push...) of whichever synced last, and the order isn't guaranteed. The risk tags are set
per Service in Terraform, so classify the Service by its most sensitive repository. To grade each repository
separately, use the GitHub Repository component package.

## Property aliases

OpsLevel derives a property's alias from its name (`GitHub Repo ID` → `github_repo_id`), and the integration
writes by alias. After apply, compare the `expected_property_aliases` output with Settings → Service properties.
If one differs, the integration reports it as a warning; fix the name or alias and re-apply.

## Choosing between the two packages

See [../README.md](../README.md#choosing-a-package).

## Risk tags

Each Service in `service_classifications` (keyed by Service alias) gets three tags:

| Tag | Values |
|---|---|
| `data_classification` | public, internal, confidential, restricted |
| `external_interface_type` | none (library, batch job, docs), internal_api (only internal callers), public_api (reachable from outside), public_web (a site or app end users open) |
| `risk_priority` | P1–P4; set it per Service, or leave it out to use the suggested default below |

Suggested default for `risk_priority` (impact × exposure; a starting point to adjust, not from a published standard):

| Data classification | Public interface (`public_api`, `public_web`) | `internal_api` / `none` |
|---|---|---|
| confidential / restricted | P1 | P2 |
| internal | P2 | P3 |
| public | P3 | P4 |

```hcl
service_classifications = {
  "payments_api" = { data_classification = "restricted", external_interface_type = "public_api" }   # P1
  "docs_site"    = { data_classification = "public", external_interface_type = "public_web" }       # P3
}
```

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
- `Languages` holds the primary language only.
- Not created: properties nothing syncs from GitHub (CodeQL status, branch rules, contributors); add them with
  their own source when something populates them.
- Classification is kept in Terraform, not GitHub, so it can drift from reality unless someone owns updating it.

## Potential additions: classification from GitHub custom properties

Instead of tags set in Terraform, the classification can come from each repository in GitHub. This needs
configuring custom properties in GitHub first:

1. In the GitHub org settings, create the custom properties `data_classification` and `external_interface_type`
   (single select, values above) and set them on each repository.
2. Add `github_data_classification` / `github_external_interface_type` (and a computed `github_risk_priority`) to
   `properties.tf`, and map them in the transform from `.custom_properties.data_classification // null` and
   `.custom_properties.external_interface_type // null`. The token's Metadata: Read permission already covers them.
3. Point the Bronze checks and the P1/P2 filter at the properties instead of the tags, and drop
   `service_classifications`. Several repos on one Service then overwrite each other's classification (last synced
   wins), which tags avoid.
