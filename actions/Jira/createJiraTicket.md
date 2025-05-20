# OpsLevel Action: Create Jira Ticket via Jira API

This OpsLevel Action enables users to create a Jira ticket directly from the OpsLevel UI using the Jira Cloud REST API. It provides a customizable form and securely authenticates using an API token stored in OpsLevel secrets.

This README provides instructions on how to configure an OpsLevel Action that allows users to create Jira tickets directly from the OpsLevel portal. This action streamlines the process of submitting bugs, enhancements, or other requests, integrating directly with your Jira instance

---

## 📋 Form Inputs

| Identifier       | Display Name    | Type       | Description                        | Required |
| ---------------- | --------------- | ---------- | ---------------------------------- | -------- |
| summary          | Summary         | Text Input | Maps to the Jira issue summary     | ✅        |
| description      | Description     | Text Area  | Maps to the Jira issue description | ✅        |
| issue\_type      | Issue Type      | Dropdown   | Choose "bug" or "enhancement"      | ✅        |
| submitting\_team | Submitting Team | Dropdown   | Populated from OpsLevel teams      | ✅        |

Defaults:

* issue\_type defaults to bug
* Teams list is populated dynamically using OpsLevel’s resource binding for teams

```
---
version: 1
inputs:
  - identifier: summary
    displayName: Summary
    description: Maps to JIRA summary.
    type: text_input
    required: true
  - identifier: description
    displayName: Description
    description: Maps to JIRA description.
    type: text_area
    required: true
  - identifier: issue_type
    displayName: Issue Type
    description: Bug / Enhancement request.
    type: dropdown
    required: true
    defaultValue: bug
    values:
      - bug
      - enhancement
  - identifier: submitting_team
    displayName: The team submitting the ticket
    description: This input is populated from teams data from OpsLevel.
    type: dropdown
    binding:
      resource: teams
    required: true
```
---

## 🔐 Authorization

This Action uses an OpsLevel secret named jira\_auth for authenticating API requests. This should be a Base64-encoded Basic Auth token (e.g., [user@example.com](mailto:user@example.com)\:api\_token).

Authorization header:

```Authorization: {{ 'jira\_auth' | secret }}```

The secret can be generated using -

```Basic $(echo -n "<user-email>:<jira-api-token>" | base64)"```

---

## 📤 Request Configuration

Endpoint:

POST [https://your-domain.atlassian.net/rest/api/3/issue](https://your-domain.atlassian.net/rest/api/3/issue)

Payload:
```
{
  "fields": {
    "project": {
      "key": "SMS"
    },    
    "description": {
      "content": [
        {
          "content": [
            {
              "text": "{{ manualInputs.description }}",
              "type": "text"
            }
          ],
          "type": "paragraph"
        }
      ],
      "type": "doc",
      "version": 1
    },
    "labels": [
      "bugfix",
      "blitz_test"
    ],
    "summary": "{{ manualInputs.summary }}",
    "issuetype": {
      "name": "Task"
    }
  }
}
```
Notes:

* Replace SMS with your actual Jira project key
* Labels are hardcoded but can be updated to reflect your team's taxonomy
* The issue type is currently hardcoded to Task — see below for dynamic mapping

---

## 🛠️ Optional: Dynamic Issue Type Mapping

To allow user selection of issue type (e.g., Bug, Task, Epic), replace the static value:
```
"issuetype": {
"name": "Task"
}

with:

"issuetype": {
"name": "{{ manualInputs.issue\_type }}"
}
```
Ensure that the dropdown values match the names of issue types defined in your Jira project.

---

## ✅ Success & Error Messaging

On successful ticket creation:
```
{% if status == "SUCCESS" %}

🎉 Congratulations!

Jira ticket {{ response.body.key }} created.
View it \[here]\([https://your-domain.atlassian.net/browse/{{](https://your-domain.atlassian.net/browse/{{) response.body.key }})

{% else %}

⚠️ Something went wrong

There was a problem creating the Jira ticket.
Please contact the team responsible for maintaining this Action.
{% endif %}
```

---
- Conditional Logic ```({% if status == "SUCCESS" %})```: Checks if the API call was successful.
- Success Message:
    - Displays a congratulatory message.
    - Includes the Jira ticket key ```({{ response.body.key }})``` from the API response.
    - Provides a direct hyperlink to the created Jira ticket using a combination of a base URL and the dynamically retrieved Jira key: <a href="https://your-domain.atlassian.net/browse/{{ response.body.key }}">here</a>.
- Failure Message: Displays a generic error message if the action fails.

## Optional: Approvals and Restrictions
- Restrictions: You can limit who can trigger this action (e.g., only Admins).
- Approvals: Add an approval step, specifying teams or users who must approve the request before it's executed.

## How to Use
- Once configured in OpsLevel, navigate to the Self-Service > Actions section.
- Find and click on the "Create Jira Ticket" action.
- Fill out the form with the summary, description, issue type, and submitting team.
- Click "Execute."
- The action will process, and a success or failure message will be displayed, including a direct link to the Jira ticket if successful.

## Notes
- Jira API Token Security: Always ensure your Jira API token is securely stored in OpsLevel Secrets.
- Jira Domain: Double-check that the Jira domain in the API endpoint and the response message URL is correct for your organization.
- Jira Project Key: Ensure the project.key in the payload matches an existing project in your Jira instance.
- Jira Issue Types: Verify that the issuetype.name in the payload ("Task") is a valid issue type in your Jira project.
- Asynchronous Actions: For long-running or complex integrations, consider using asynchronous actions where OpsLevel provides a webhook for status updates.

## 📎 Prerequisites

* OpsLevel account with Action support
* Jira Cloud account with API access
* A valid API token stored in OpsLevel Secrets as jira\_auth
* A Jira project with issue creation permissions

---