# Export services in OpsLevel into a csv file ordered by last updated time

This script is designed to export the basic details (name, id and last updated time) of all the services in OpsLevel into a csv file

Requirements:

- Python 3.10.10
- `requests` library is installed
- `pandas` library is installed

To run this:

1. Update your api token in the script or set it up as an environment variable
2. Execute the commands below. 

```bash
python ./export_services_as_csv.py
```