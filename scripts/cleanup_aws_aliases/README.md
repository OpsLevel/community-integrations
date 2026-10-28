# Clean Up Aliases After Prefixing AWS Component Names

When an AWS component name collides with another component's alias, a common fix is to add a prefix such as `aws-` to the `name` expressions in the AWS integration's transform definition. After the next sync, each component is renamed and gets a new locked primary alias from its new name, for example `aws-cards-prod-webhooks-0`. The alias from the old name, `cards-prod-webhooks-0`, stays on the component as a regular alias, so the original name is still taken.

This script finds and deletes those leftover aliases in bulk, or you can modify it to fit your needs.

For every component that has both an alias `<prefix>X` and an alias `X`, it deletes `X`. It never deletes:

- a component's primary alias (slug)
- ARN aliases such as `arn:aws:rds:…`
- the new prefixed aliases
- aliases on other components (it only looks at aliases on the same component)

Deleting an alias can't be undone automatically, but you can add the alias back by hand at any time.

## Requirements

- Python 3
- The `requests` library installed
- A read-write API token, which must be created by an admin

## To run this

1. Add your API token to an `OPSLEVEL_API_TOKEN` environment variable.
2. If you are on self-hosted OpsLevel, add your GraphQL endpoint to an `OPSLEVEL_ENDPOINT` environment variable, for example `https://<your-opslevel-host>/graphql`.
3. Run the commands below.

## cleanup_aws_aliases.py

The script `cleanup_aws_aliases.py` goes through every component in the account and lists the leftover aliases. By default it runs as a dry run and doesn't delete anything:

```
python ./cleanup_aws_aliases.py
```

Example output:

```
Found 1 alias(es) eligible for deletion
[dry-run] Would delete: cards-prod-webhooks-0 (component: aws-cards-prod-webhooks-0)
Dry run complete; nothing was deleted. Re-run with --apply to delete the aliases above.
```

If you used a prefix other than `aws-`, pass it with `--prefix`:

```
python ./cleanup_aws_aliases.py --prefix svc-
```

Once you've reviewed the list, run the script with `--apply` to delete the aliases:

```
python ./cleanup_aws_aliases.py --apply
```

If OpsLevel rate limits the API token, the script waits as long as OpsLevel asks and then retries, so large accounts may take several minutes. If an alias fails to delete, the script logs the error and continues with the rest.

## After cleanup

Deleting an alias only frees the name. If another component should own that name, for example one defined in `opslevel.yml` that ended up as `my-service_2`, add the alias to that component in the UI or in its `opslevel.yml`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success, including dry runs and runs with nothing to delete |
| 1 | One or more aliases failed to delete |
| 2 | Nothing was deleted because of a setup problem, for example a missing token or a failed API request while listing components |
