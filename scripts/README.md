# Custom Scripts Library

## Overview
Custom code written by our customers for the purpose of integrating with OpsLevel.
For example, you might find scripts for importing service dependency mapping from
a third party tool, extending our Jira integration to automatically create Jira
tickets from Campaign Checks, or populating your software catalog with
infrastructure resources from GCP.

### Taskfile tasks

[Taskfile](https://taskfile.dev/) tasks can be used to lint, format, test, and run
scripts found in this directory.
With [task installed](https://taskfile.dev/installation/) run `task --list` for examples.

### Python Scripts

Create Campaign Jira Issues.
- [./create_campaign_jira_issues/](./create_campaign_jira_issues/)

### Ruby Scripts

Import GCP infrastructure into your OpsLevel account.
- [./gcp_infrastructure_import/](./gcp_infrastructure_import/)
