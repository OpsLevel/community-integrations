# Delete Deactivated Users

This script permanently deletes deactivated users from your OpsLevel account. Users deactivated in OpsLevel, either manually or through SCIM, stay in the account until they are deleted. Use this script to clean them up in bulk, or modify it to fit your needs.

**Deletion is permanent and cannot be undone.** Deleting a user removes their team memberships, contacts, tags and notification subscriptions, and removes their name from historical records such as action runs and approvals.

## Requirements:

* Python 3.11
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

If an `--exclude` email does not match any user in the account, for example because of a typo, the script stops without deleting anything.

Once you have reviewed the list, run the script with `--apply`. It will prompt you to type `delete` to confirm you want to delete all users on the list:

```
python ./delete_deactivated_users.py --apply
```

When the script runs automatically, for example from cron or a CI pipeline, there is no one to answer the prompt, so the script stops without deleting anything. Add `--yes` to skip the prompt:

```
python ./delete_deactivated_users.py --apply --yes
```

If OpsLevel rate limits the API token, the script waits for the time OpsLevel asks for and retries, so large accounts may take several minutes. If a user fails to delete, the script logs the error and continues with the remaining users.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success, including dry runs and runs with nothing to delete |
| `1` | One or more users failed to delete |
| `2` | Nothing was deleted because of a setup problem, for example a missing token, an unmatched `--exclude` email, a missing `--yes`, or confirmation not given |
