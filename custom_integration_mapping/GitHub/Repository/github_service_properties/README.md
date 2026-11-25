# Option B: GitHub properties on Service

Adds GitHub repository metadata to your existing **Services** as custom properties, kept up to date by a pull
custom integration. No new component type: owners see the data on the services they already own.

> **Status:** less tested than the [GitHub Repository component](../github_repository_component/) package, which has
> been applied end to end. The derived property aliases (below) haven't been confirmed against a live account, so
> run `terraform plan` and check the `expected_property_aliases` output after the first apply.

## What it creates

| Resource | Details |
|---|---|
| 10 custom properties on the default component type (Service), prefixed `github_` | Set by the integration, locked in the UI and not allowed in `opslevel.yml` |
| Custom integration **Integration Data Mapping (Pull) - GitHub Repo Metadata on Services** | Polls `GET /orgs/<org>/repos` and writes each repository's metadata onto its Service. Creates nothing; repositories with no matching Service are skipped |
| Secret `github_api_token` (optional) | The GitHub token the integration reads. Not created by default: create it in OpsLevel, or set `manage_secrets = true` and `github_token` |

Properties: GitHub Repo ID, Full Name, Description, Visibility, Archived, Empty, Created At, Last Pushed At,
Age In Months, Topics. The extract and transform definitions are in
[`modules/github_service_properties/definitions/`](modules/github_service_properties/definitions/).

## How a repository is matched to a Service

1. Optional: the repository's `opslevel_service` GitHub custom property, if your org defines it: the Service's alias.
2. Otherwise the repository name, lowercased, with `-` turned into `_` (`shopping-cart-service` →
   `shopping_cart_service`).

Repositories that match no Service are skipped (they show as warnings on the integration). Set `opslevel_service`
on repositories whose name doesn't match. One repository maps to one Service; a monorepo's metadata goes to one
service only.

**Several repositories on one Service:** the integration writes each repository in turn, so the Service keeps the
metadata (visibility, last push...) of whichever synced last, and the order isn't guaranteed. To keep each
repository separate, use the [GitHub Repository component](../github_repository_component/) package.

## Property aliases

OpsLevel derives a property's alias from its name (`GitHub Repo ID` → `github_repo_id`), and the integration
writes by alias. After apply, compare the `expected_property_aliases` output with Settings → Service properties.
If one differs, the integration reports it as a warning; fix the name or alias and re-apply.

## Deploy

```bash
cd example
cp terraform.tfvars.example terraform.tfvars   # GitHub org, owner team (and the token, if Terraform creates the secret)
export OPSLEVEL_API_TOKEN=...
terraform init && terraform plan && terraform apply
```

Then open the new integration in OpsLevel and click **Sync** (it also polls on its own schedule).

To grade the services on their repository, add the [risk scorecard](../risk_scorecard/).
