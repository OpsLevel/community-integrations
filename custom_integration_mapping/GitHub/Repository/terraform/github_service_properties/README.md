# OpsLevel package: GitHub properties on Service

Adds GitHub repository metadata to your existing **Services** as custom properties and grades the services on
risk-based standards. No new component type: owners see the data and the scorecard on the services they already own.

> **Status:** less tested than the [GitHub Repository component](../github_repository_component/) package, which has
> been applied end to end. The derived property aliases (below) haven't been confirmed against a live account, so
> run `terraform plan` and check the `expected_property_aliases` output after the first apply.

## What it creates

| Resource | Details |
|---|---|
| 14 custom properties on the default component type (Service), prefixed `github_` | Set by the integration, locked in the UI (below) |
| Custom integration **Integration Data Mapping (Pull) - GitHub Repo Metadata on Services** | Polls `GET /orgs/<org>/repos` and writes each repository's metadata onto its Service. Creates nothing; repositories with no matching Service are skipped |
| Secret `github_api_token` | The GitHub token the integration uses (`manage_secrets = false` to reuse an existing one) |
| Filters | **Services with a GitHub repo (active)** and **Services with a GitHub repo - High risk (P1/P2)** |
| Scorecard **(Use Case) Security - Service GitHub Repository Risk** | 7 Custom Property checks ([main guide](../../README.md#part-5-scorecard)) |

Properties: GitHub Repo ID, Full Name, Description, Visibility, Archived, Empty, Created At, Last Pushed At,
Age In Months, Languages, Topics; GitHub Data Classification, External Interface Type, Risk Priority.

## How a repository is matched to a Service

1. The repository's `opslevel_service` GitHub custom property, if set: the Service's alias.
2. Otherwise the repository name, lowercased, with `-` turned into `_` (`shopping-cart-service` →
   `shopping_cart_service`).

Repositories that match no Service are skipped (they show as warnings on the integration). Set `opslevel_service`
on repositories whose name doesn't match. One repository maps to one Service; a monorepo's metadata goes to one
service only.

**Several repositories on one Service:** the integration writes each repository in turn, so the Service keeps the
values of whichever synced last. A P1 repository can be hidden behind a P4 one, and the order isn't guaranteed.
Point only the repository that represents the Service at it (set `opslevel_service` on that one, and give the
others an `opslevel_service` that matches no Service, e.g. `none`), or use the GitHub Repository component package,
which grades each repository separately.

## Property aliases

OpsLevel derives a property's alias from its name (`GitHub Repo ID` → `github_repo_id`), and the integration
writes by alias. After apply, compare the `expected_property_aliases` output with Settings → Service properties.
If one differs, the integration reports it as a warning; fix the name or alias and re-apply.

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

- Reads every repository in the org, 100 per request, following GitHub's `Link` header to the next page.
- `Languages` holds the primary language only.
- Not created: properties nothing syncs from GitHub (CodeQL status, branch rules, contributors); add them with
  their own source when something populates them.
