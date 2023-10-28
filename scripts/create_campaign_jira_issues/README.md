# Create Campaign Jira Issues

This script is designed to create Jira issues for each service
in a campaign from information associated with the service's team.
To know the appropriate Jira project to create against,
the script assumes that each team will have a "jira" contact
that contains the URL to the team's Jira project.

To run this:

1. Modify `JIRA_URL` to use your company's Atlassian instance.
2. Create a `.env` file containing values for `JIRA_USER`, `JIRA_APITOKEN`,
   and `OPSLEVEL_APITOKEN` (see the [dotenv docs](https://pypi.org/project/python-dotenv/)
   for information on the format).
3. Execute the commands below. The examples assume a Linux/macOS-like shell.


```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_campaign_jira_issues.py <OpsLevel campaign URL>
```
