# Convert Users roles

These scripts are designed to convert user roles depending on your use case. Use the script that best matches your use case, or modify to fit your needs. See the list of available scripts and explanations below.

Requirements:

- Python 3.10.10
- `requests` library is installed

To run this:

1. Add your api token to an `OPSLEVEL_API_TOKEN` environment variable
2. Execute the command mentioned as per the scripts below

## convert_user_to_team_member_roles.py

The script `convert_user_to_team_member_roles.py` will query for all users in the account, list them out and prompt you to confirm you want to convert all users on the list to a team member role.

```bash
python ./convert_user_to_team_member_roles.py
```
