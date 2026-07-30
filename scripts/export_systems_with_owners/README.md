# Export Systems with Owners to CSV

This script is designed to fetch all Systems in your OpsLevel account, along with their owning Team, and export the results to a CSV file.

Prerequisites:

- Systems must exist in your OpsLevel account.
- Owner will be blank in the output for Systems with no Team assigned as owner, or with a non-Team owner.

Requirements:

- Python 3.10.10 or higher
- `requests` & `csv` libraries are installed

To run this:

1. Add your api token to an `OPSLEVEL_API_TOKEN` environment variable
2. Execute the command below
3. A `systems_with_owners.csv` file will be created in the same directory, containing one row per System with its name and owner.

```bash
python ./export_systems_with_owners.py
```
