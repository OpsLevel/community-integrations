# GitHub Repositories → OpsLevel Custom Integration

A **pull** custom integration that reads every repository in a GitHub organization and creates one
**GitHub Repository** component per repo in OpsLevel, with repo metadata as custom properties. Each repo is then
classified with three OpsLevel tags (`data_classification`, `external_interface_type`, `risk_priority`) and graded
on a risk-based scorecard.

OpsLevel doesn't run maturity checks on the repository object itself, so a component per repository is what makes
repository-level checks possible.

## Overview

```text
GitHub REST API: GET /orgs/<org>/repos   (polled by OpsLevel on a schedule, every page)
  ↓
OpsLevel Custom Integration (pull)
  ↓
Extractor YAML: one record per repo (external_kind github_repos)
  ↓
Transform YAML: repo metadata as properties
  ↓
"GitHub Repository" components (one per repo)  +  risk tags you set (UI or Terraform)
  ↓
Filters + "(Use Case) Security - GitHub Repository Risk" scorecard
```

Nothing runs on your infrastructure: OpsLevel calls the GitHub API with a token stored as an OpsLevel secret.

## Set it up

| Option | Use it when |
|---|---|
| **[Step-by-step guide](step_by_step_setup.md)** | You want to see and adjust each piece. Two stdlib-only Python scripts create the component type and the scorecard through the GraphQL API; the integration is pasted in the UI and tags are set in the UI. |
| **[Terraform](terraform/)** | You want everything (component type, secret, integration, risk tags, filters, scorecard) created and kept in code. Classifications live in one map in your tfvars, which suits classifying many repos. Also includes an alternative package that writes the metadata onto your existing **Services** instead of creating new components. |

## What you get

- **GitHub Repository** component type (`github_repository`) with 11 properties synced from GitHub: name,
  description, visibility, archived, empty, creation and last-push dates, age in months, primary language, topics.
  Components are identified by the GitHub repo id, so renamed repos keep their component.
- **Risk tags** on each component: `data_classification`, `external_interface_type` and `risk_priority` (P1–P4,
  with a [suggested default](step_by_step_setup.md#risk-priority) from the other two).
- **Scorecard** *(Use Case) Security - GitHub Repository Risk*: 7 checks from "classified" (Bronze) to "low risk
  and actively maintained" (Diamond), with the strictest controls applying only to P1/P2 repos.
  [Full list](step_by_step_setup.md#part-6-scorecard).

## Files

| File | What it is |
|---|---|
| [`step_by_step_setup.md`](step_by_step_setup.md) | The manual setup guide, with troubleshooting |
| [`extract_definition.yaml`](extract_definition.yaml) | Extractor: polls `GET /orgs/<your_github_org>/repos`, following every page |
| [`transform_definition.yaml`](transform_definition.yaml) | Transform: one `github_repository` component per repo, 11 properties |
| [`example_github_api_response.json`](example_github_api_response.json) | Sample GitHub response (3 fictional repos) to test the transform's jq locally |
| [`scripts/create_github_repository_type.py`](scripts/create_github_repository_type.py) | Creates or updates the component type and its 11 properties (dry run unless `--apply`) |
| [`scripts/create_github_repository_scorecard.py`](scripts/create_github_repository_scorecard.py) | Creates the 3 filters, the scorecard and its 7 checks (dry run unless `--apply`) |
| [`terraform/`](terraform/) | Terraform / OpenTofu packages for the whole setup |

## Limits

- **Primary language only.** `top_languages` holds `.language`; the full list needs `/repos/{repo}/languages` per repo.
- **Classification is kept in OpsLevel, not GitHub,** so it can drift from reality unless someone owns updating it.
- **No automatic link** between a repo component and the component it belongs to (see [Part 7](step_by_step_setup.md#part-7-link-repos-to-their-components)).

## Potential additions

### Classification from GitHub custom properties

Instead of tags set in OpsLevel, the classification can live in GitHub and be synced like the other metadata. This
needs configuring custom properties in GitHub first:

1. In **GitHub → Organization settings → Custom properties**, create `data_classification` and
   `external_interface_type` (single select, values above) and set them on each repository: by hand, through the
   API, or from a file in each repo with a workflow (tick **Allow repository actors to set this property** for the
   workflow route).
2. Add properties for them to the component type, and map them in the transform:
   `data_classification: .custom_properties.data_classification // null`, likewise for
   `external_interface_type`. Compute `risk_priority` in the transform with jq from the two values. The org repos
   endpoint already returns `custom_properties`; the token's Metadata: Read permission is enough to read them.
3. Point the Bronze checks and the P1/P2 filter at the properties instead of the tags.

### Extending the integration

- **More properties from the same payload.** The transform receives the full repo object, so properties such as
  `default_branch: .default_branch` or `has_issues: .has_issues` only need a property on the type and a line in the
  transform. Add them to `PROPERTIES` in the type script too.
- **Properties the org endpoint doesn't return** (CodeQL status, branch rulesets, top contributors) need per-repo
  API calls or a separate integration; add them with their own source, then add checks for them (for example, CodeQL
  enabled on P1/P2 repos).
- **Automatic repo → component link.** Two options: (1) a GitHub custom property such as `opslevel_service` mapped to
  a property and matched by a managed relationship rule; (2) a second extractor polling OpsLevel's GraphQL API for
  each component's attached repositories, writing the owning component's alias onto the repo component, plus an
  "array contains" managed relationship rule.
- **Metadata on Services instead of new components.** See the
  [`github_service_properties`](terraform/github_service_properties/) Terraform package.
