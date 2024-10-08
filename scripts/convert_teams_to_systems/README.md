# Convert teams to systems

This script is designed to convert existing teams in an OpsLevel account to systems. It also is a good example of leveraging the OpsLevel GraphQL APIs to automate some of the account updates\chores.

Requirements:

- Python 3.10.10
- `requests` library is installed
- `json` library is installed

To run this:

1. Update your api token in the script or set it up as an environment variable
2. Execute the commands below. 

```bash
python ./export_services_as_csv.py
```