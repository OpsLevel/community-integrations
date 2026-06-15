# Remove a Custom Property Across OpsLevel Infra Types

`remove_custom_property.py` deletes a custom property (default: `name`) from all
AWS-backed infrastructure component types via the OpsLevel GraphQL API. Each type
holds its own copy of the property, so the script finds all infra components and deletes each
one (`propertyDefinitionDelete` — there's no bulk mutation). Dry-run by default.

## Setup
```
pip install requests
export OPSLEVEL_API_TOKEN=xxxxxxxx
```

## Run

```
python3 remove_custom_property.py          # 1. dry run: confirms matches, deletes nothing
# edit PREFIX="aws_dynamodb", APPLY=True   # 2. delete one type first to confirm it works
# edit PREFIX="aws_", keep APPLY=True      # 3. run the rest
```
Output per type: would delete <id> (dry run), deleted, FAILED [...], or no 'name' (skipped). No bulk rollback, so the log is your record.
## Config (top of file)

- `PROP` — property to remove (alias or name). Default `name`.
- `PREFIX` — alias prefix that marks a type as "infra". Default `aws_` (the API has no infra filter, so we match by prefix).
- `APPLY` — `False` = dry run, `True` = delete.

## Notes

- Deletes are **irreversible** and drop stored values — dry-run, test one, then run all.
- `name` ("The name of the resource") may be a built-in field; a `FAILED` line means the API protects it. To hide instead of delete, use `propertyDefinitionUpdate` with `propertyDisplayStatus: hidden`.
