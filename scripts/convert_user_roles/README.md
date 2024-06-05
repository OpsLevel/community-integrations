# Convert Users roles

This contains the following script(s):

- `convert_user_to_team_member_roles.py`

These scripts are designed to convert user roles depending on your use case. Use the script that best matches your use case, or modify to fit your needs.

Requirements:

- Python 3.10.10
- `requests` library is installed

To run this:

1. Add your api token to an `OPSLEVEL_API_TOKEN` environment variable
2. Execute the command below and choose which property you want to convert by entering the integer value in the list.

```bash
python ./convert_tags_to_custom_properties.py
```

## convert_user_to_team_member_roles.py

This script will query for all users in the account, list them out and prompt you to convert all users on the list to a team member role.