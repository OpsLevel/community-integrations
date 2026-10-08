# Delete Deactivated Users

This script permanently deletes deactivated users from your OpsLevel account. Users deactivated in OpsLevel, either manually or through SCIM, stay in the account until they are deleted. Use this script to clean them up in bulk, or modify it to fit your needs.

**Deletion is permanent and cannot be undone.** Deleting a user removes their team memberships, contacts, tags and notification subscriptions, and removes their name from historical records such as action runs and approvals.

## Requirements:

* Python 3.8 or later
* `requests` library is installed
* An API token belonging to an admin user

## To run this:

1. Add your api token to an `OPSLEVEL_API_TOKEN` environment variable
2. If you are on self-hosted OpsLevel, add your GraphQL endpoint to an `OPSLEVEL_ENDPOINT` environment variable, for example `https://<your-opslevel-host>/graphql`
3. Execute the commands mentioned below

## delete_deactivated_users.py

The script `delete_deactivated_users.py` will query for all deactivated users in the account and list them out. By default it runs as a dry run and does not delete anything.

```
python ./delete_deactivated_users.py
```

To keep specific users, exclude them by email. Repeat `--exclude` for each user:

```
python ./delete_deactivated_users.py --exclude jane@example.com --exclude sam@example.com
```

Once you have reviewed the list, run the script with `--apply`. It will prompt you to type `delete` to confirm you want to delete all users on the list:

```
python ./delete_deactivated_users.py --apply
```

To run the script without the confirmation prompt, for example from a scheduler, add `--yes`:

```
python ./delete_deactivated_users.py --apply --yes
```

If a user fails to delete, the script logs the error and continues with the remaining users. It exits with code `1` if any deletion failed.
