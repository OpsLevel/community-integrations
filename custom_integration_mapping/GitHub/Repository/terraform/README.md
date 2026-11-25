# Terraform: GitHub repository metadata in OpsLevel

Two Terraform (or OpenTofu) packages that set up everything in the [step-by-step guide](../step_by_step_setup.md) with `terraform apply`:
component type or properties, the custom integration, the GitHub token secret, filters, and the risk scorecard.
Both pull the same GitHub data and classify risk with the same OpsLevel tags (`data_classification`,
`external_interface_type`, `risk_priority`) set from a map in your tfvars; they differ in where the data lands.

| Package | What it does |
|---|---|
| [`github_repository_component/`](github_repository_component/) (recommended) | One **GitHub Repository** component per repo. Same setup as the main guide. |
| [`github_service_properties/`](github_service_properties/) | `github_*` custom properties on your existing **Services**. No new components. |

Pick one. Both create a secret with the same alias (`github_api_token`), so to switch, `terraform destroy` the first
one before applying the other (or give one of them a different `github_token_secret_alias`).

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

## Deploy

```bash
cd github_repository_component/example      # or github_service_properties/example
cp terraform.tfvars.example terraform.tfvars  # GitHub org, owner team alias, GitHub token, classifications
export OPSLEVEL_API_TOKEN=...                 # OpsLevel API token with write access
# export OPSLEVEL_API_URL=https://<subdomain>.opslevel.com   # only if your account isn't on app.opslevel.com
terraform init && terraform plan && terraform apply
```

Then open the new custom integration in OpsLevel and click **Sync**.

With the component package on a new account, the risk tags go on components the first sync creates: `apply`
(leave `repo_classifications` empty or expect tag errors), **Sync**, then `apply` again to add the tags.

Requirements: Terraform / OpenTofu ≥ 1.5, OpsLevel provider ≥ 1.14, a team for `owner_team_alias`, and rubric levels
with index 1–3 (set `rubric_level_count = 4` if your rubric also has a Diamond level). If the secret already exists
in your account, set `manage_secrets = false`. `terraform.tfvars` holds your GitHub token: keep it out of version
control (each package's `.gitignore` already excludes it).

## Known issues

- OpsLevel provider v1.14.x fails to create a component type property whose `description` is `""` ("Provider
  produced inconsistent result after apply"). Every property in these packages has a description; keep it that way
  if you add more.
- `opslevel_component_type` doesn't expose property definition ids, so option A's filters reference properties by
  alias in `key_data` (the API accepts it; confirmed working). Option B and the Python scripts use the property
  definition id.
- `opslevel_service_tag` needs a component alias. The component package uses the alias OpsLevel derives from the
  component name (`github_repo_-_<repo>`), not the integration's `github_repo_<id>` identifier, because Terraform
  doesn't know GitHub repo ids.
- `opslevel_property_definition` has no `alias` argument and always targets the default component type, so option B
  assumes the alias OpsLevel derives from each property name (see its README).
