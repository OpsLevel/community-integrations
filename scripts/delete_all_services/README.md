# Delete all infrastructure

This bash script will delete all services resources created via API. It will prompt you to confirm you want to delete all services resources. Please note that service that is locked by a service config will not be deleted

Requirements:

- opslevel CLI is installed https://github.com/OpsLevel/cli

To run this:

1. Ensure you have an `OPSLEVEL_API_TOKEN` environment variable as per the [CLI documentation](https://github.com/OpsLevel/cli?tab=readme-ov-file#prerequisite)
2. Execute the command mentioned as per the scripts below

## delete_services.sh

The script `delete_services.sh` provides 2 options. 

* Option 1 will list out all services by name and id and report the number of resources. 
* Option 2 will query for all services resources in the account, report the number of resources and prompt you to confirm you want to delete all services.

```bash
bash ./delete_services.sh
```