# Export opslevel.yml files for all services

This script is designed to export the auto-generated opslevel.yml contents for
each service in your OpsLevel account. The contents are written to:

```
opslevelyml_repo/<componentType>/<service_slug>/opslevel.yml
```

For example:

```
opslevelyml_repo/service/shopping_cart_service/opslevel.yml
opslevelyml_repo/backend/fraud_detection_service/opslevel.yml
```

The script can be updated to push/copy the opslevel.yml file to the 
coresponding service's repo (and maybe automatically open a pull/merge request)
in the git repository.

The script excludes the `properties:` section from exported YAML by default. Use
`--include properties` to keep it.

Components without a linked repository are skipped by default. Their OpsLevel
`htmlUrl` is written to `skipped_components_with_missing_repo_links.txt`. Use
`--include-no-repo` to export those components as well.

Use `--dry-run` to preview which components would be exported without writing
`opslevelyml_repo/`. The skipped-components file is still written in dry-run mode
unless `--include-no-repo` is set.

Requirements:

- Python 3.10.10
- `requests` library is installed

To run this:

1. Add your api token to an `OPSLEVEL_API_TOKEN` environment variable
2. Run the script. You will be prompted to select which component types to export,
   unless you pass `--component-types` for non-interactive use.

```bash
python ./opslevel_yml_export_for_all_services.py
python ./opslevel_yml_export_for_all_services.py --include properties
python ./opslevel_yml_export_for_all_services.py --dry-run
python ./opslevel_yml_export_for_all_services.py --include-no-repo
python ./opslevel_yml_export_for_all_services.py --component-types service backend frontend
```

When prompted, enter comma-separated numbers for the component types you want,
or `a` to export all default component types.

Example:

```
python opslevel_yml_export_for_all_services.py

Select component type(s) to export opslevel.yml for (comma-separated numbers, or enter 'a' for all):
1. api
2. application
3. archived_component
4. backend
5. frontend
6. jira_ticket
7. library
8. mobile_app
9. service
10. team_checks
11. third_party_vendors
12. unowned_repo
> 1,2,4,5,7,8,9,11

Exporting opslevel.yml for: api, application, backend, frontend, library, mobile_app, service, third_party_vendors

Exported 24 component(s) to /export_all_opslevel_yml/opslevelyml_repo.
Skipped 57 component(s) with no linked repo. See /export_all_opslevel_yml/skipped_components_with_missing_repo_links.txt.
```
