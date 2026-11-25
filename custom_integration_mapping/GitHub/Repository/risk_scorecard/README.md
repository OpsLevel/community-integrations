# Extended usage: risk classification and scorecard

Builds on the [GitHub Repositories custom integration](../README.md) to classify each repository by risk and grade
it on a scorecard. Works with either option:

| Module | Builds on | Tags and grades |
|---|---|---|
| [`modules/github_repository_risk`](modules/github_repository_risk/) | [A. GitHub Repository component](../github_repository_component/) | Each GitHub Repository component |
| [`modules/github_service_properties_risk`](modules/github_service_properties_risk/) | [B. GitHub properties on Service](../github_service_properties/) | Each Service with GitHub repo metadata |

## What it adds

| Resource | Details |
|---|---|
| Risk tags | `data_classification`, `external_interface_type` and `risk_priority` on each repo component (or Service), from a classifications map in your tfvars |
| Filters | **active** (not archived), **risk_priority P1 or P2** (tag) and **High risk (P1/P2)** (both) |
| Scorecard **(Use Case) Security - GitHub Repository Risk** (option B: **… Service GitHub Repository Risk**) | 7 checks: 4 Tag Defined checks on the risk tags, 3 Custom Property checks on the synced metadata (below) |

## Risk tags

| Tag | Values |
|---|---|
| `data_classification` | public, internal, confidential, restricted |
| `external_interface_type` | none (library, batch job, docs), internal_api (only internal callers), public_api (reachable from outside), public_web (a site or app end users open) |
| `risk_priority` | P1–P4; set it per repository (or Service), or leave it out to use the suggested default below |

Suggested default for `risk_priority` (impact × exposure; a starting point to adjust, not from a published standard):

| Data classification | Public interface (`public_api`, `public_web`) | `internal_api` / `none` |
|---|---|---|
| confidential / restricted | P1 | P2 |
| internal | P2 | P3 |
| public | P3 | P4 |

Option A, keyed by GitHub repository name:

```hcl
repo_classifications = {
  "payments-api" = { data_classification = "restricted", external_interface_type = "public_api" }   # P1
  "docs-site"    = { data_classification = "public", external_interface_type = "public_web" }       # P3
  "legacy-batch" = { data_classification = "internal", external_interface_type = "none", risk_priority = "P2" }
}
```

Option B, keyed by Service alias (classify a Service by its most sensitive repository):

```hcl
service_classifications = {
  "payments_api" = { data_classification = "restricted", external_interface_type = "public_api" }   # P1
  "docs_site"    = { data_classification = "public", external_interface_type = "public_web" }       # P3
}
```

## Scorecard checks

| Level | Check | Applies to |
|---|---|---|
| 1 Bronze | Data classification tag is set | all in scope |
| 1 Bronze | External interface type tag is set | all in scope |
| 2 Silver | Repository has a description | all in scope |
| 2 Silver | Not a P1 risk (`risk_priority` tag) | all in scope |
| 3 Gold | Repository is not public | P1/P2 only |
| 4 Diamond* | Pushed to in the last 90 days | P1/P2 only |
| 4 Diamond* | Risk priority P3 or lower (`risk_priority` tag) | all in scope |

\* On Gold when `rubric_level_count = 3` (the default). Checks limited to P1/P2 don't apply to lower-risk repos,
so those aren't held back by them. A Tag Defined check fails when the tag is missing, so unclassified repos stay at
Beginner. Archived repositories are out of scope.

## Deploy

### New setup

[`examples/`](examples/) has a root module per option that deploys the integration **and** the risk scorecard. Use
it instead of the integration's own example:

```bash
cd examples/github_repository_component      # or examples/github_service_properties
cp terraform.tfvars.example terraform.tfvars  # GitHub org, owner team, rubric levels, classifications
export OPSLEVEL_API_TOKEN=...
terraform init && terraform plan && terraform apply
```

**Option A on a new account:** the tags go on components the first sync creates, so `apply` with
`repo_classifications` empty, click **Sync** on the integration, then fill in `repo_classifications` and `apply`
again.

### Integration already deployed

Add the risk module to the root module you already applied (for example `github_repository_component/example`), so
Terraform keeps managing the integration in the same state:

```hcl
module "github_repository_risk" {
  source = "<path to>/risk_scorecard/modules/github_repository_risk"

  component_type_id    = module.github_repository.component_type_id
  owner_team_alias     = var.owner_team_alias
  rubric_level_count   = 3
  repo_classifications = { /* ... */ }
}
```

For option B, use `modules/github_service_properties_risk` with
`property_definition_ids = module.github_service_properties.property_definition_ids` and `service_classifications`.

Requirements: rubric levels with index 1–3 (set `rubric_level_count = 4` if your rubric also has a Diamond level).
To reclassify a repo later, edit its entry and `apply`.

## Troubleshooting

#### `apply` fails with "not found" on a risk tag

Option A attaches tags by the alias OpsLevel derives from the component name (`GitHub Repo - payments-api` →
`github_repo_-_payments-api`). Either the component doesn't exist yet (run **Sync** first), or the repo name has
characters other than letters, digits, `-` and `_` and derives a different alias: check the component's aliases in
OpsLevel.

#### Every repo fails the Bronze checks

The repo (or Service) has no risk tags yet: add it to the classifications map and `apply`.

## Known issues

- `opslevel_service_tag` needs a component alias. Option A uses the name-derived alias (`github_repo_-_<repo>`), not
  the integration's `github_repo_<id>` identifier, because Terraform doesn't know GitHub repo ids.
- `opslevel_component_type` doesn't expose property definition ids, so option A's filters and checks reference
  properties by alias (the API accepts it; confirmed working). Option B uses the property definition ids.

## Limits

- **Classification is kept in Terraform, not GitHub,** so it can drift from reality unless someone owns updating it.

## Potential addition: classification from GitHub custom properties

Instead of tags set in Terraform, the classification can live in GitHub and be synced like the other metadata. This
needs configuring custom properties in GitHub first:

1. In **GitHub → Organization settings → Custom properties**, create `data_classification` and
   `external_interface_type` (single select, values above) and set them on each repository: by hand, through the
   API, or from a file in each repo with a workflow (tick **Allow repository actors to set this property** for the
   workflow route).
2. Add properties for them to the component type (or Service), and map them in the transform:
   `data_classification: .custom_properties.data_classification // null`, likewise for
   `external_interface_type`. Compute `risk_priority` in the transform with jq from the two values. The org repos
   endpoint already returns `custom_properties`; the token's Metadata: Read permission is enough to read them.
3. Point the Bronze checks and the P1/P2 filter at the properties instead of the tags, and drop the classifications
   map.
