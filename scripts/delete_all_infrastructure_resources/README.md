# Delete all infrastructure resources created via API

This bash script will delete all infrastructure resources created via API. It will prompt you to confirm you want to delete all infrastructure resources.

Requirements:

- opslevel CLI is installed https://github.com/OpsLevel/cli

To run this:

1. Ensure you have an `OPSLEVEL_API_TOKEN` environment variable as per the [CLI documentation](https://github.com/OpsLevel/cli?tab=readme-ov-file#prerequisite)
2. Execute the command mentioned as per the scripts below

## delete_all_infrastructure_resources.sh

The script `delete_all_infrastructure_resources.sh` provides 2 options. 

* Option 1 will list out all infrastructure resources by name and id and report the number of resources. 
* Option 2 will query for all infrastructure resources in the account, report the number of resources and prompt you to confirm you want to delete all infrastructure resources.

```bash
bash ./delete_all_infrastructure_resources.sh
```