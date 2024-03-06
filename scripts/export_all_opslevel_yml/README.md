# Export opslevel.yml files for all services

This script is designed to export the auto-generated opslevel.yml contents for
each service in your OpsLevel account. The contents are written to file as:
"service name"_opslevel.yml.

The script can be updated to push/copy the opslevel.yml file to the 
coresponding service's repo (and maybe automatically open a pull/merge request)
in the git forge.

Requirements:

- Python 3.10.10
- `requests` library is installed

To run this:

1. Add your api token to OPSLEVEL_API_TOKEN
2. Execute the commands below. 

```bash
python ./opslevel_yml_export_for_all_services.py
```