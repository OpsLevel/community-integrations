# Build an Action used to create a new Incident in Pagerduty.

We're using this PagerDuty API call `POST https://api.pagerduty.com/incidents` to create the incident. The two JSON files show the JSON response from our GraphQL API for both parts of the Action config. I'll paste three of the fields below so they are easier to read and easy to copy+paste into the OpsLevel GUI.

The form submission details / customActionsTriggerDefinition.manualInputsDefinition is in YAML format:

```
---
version: 1
inputs:
  - identifier: IncidentTitle
    displayName: Title
    description: Title of the incident to trigger
    type: text_input
    required: true
    maxLength: 60
    defaultValue: Service Incident Manual Trigger
  - identifier: IncidentDescription
    displayName: Incident Description
    description: The description of the incident
    type: text_area
    required: true
```
The following headers to be included:

Content-Type: application/json
Accept: application/vnd.pagerduty+json;version=2
Authorization: Token <YOUR_TOKEN_HERE>
From: <email>

The payload / customActionsExternalAction.liquidTemplate uses Liquid syntax:

```
{
    "incident":
    {
        "type": "incident",
        "title": "{{manualInputs.IncidentTitle}}",
        "service": {
            "id": "{{ service | tag_value: 'pd_id' }}",
            "type": "service_reference"
        },
        "body": {
        "type": "incident_body",
        "details": "Incident triggered from OpsLevel by {{user.name}} with the email {{user.email}}. {{manualInputs.IncidentDescription}}"
        }
    }
}
```

The response message / customActionsTriggerDefinition.responseTemplate uses Liquid syntax:

```
{% if response.status >= 200 and response.status < 300 %}
## Congratulations!
Your request for {{ service.name }} has succeeded. See the incident here: {{response.body.incident.html_url}}
{% else %}
## Oops something went wrong
Please contact [{{ action_owner.name }}]({{ action_owner.href }}) for more help.
{% endif %}
```


More information on creating Actions can be found [in our documentation](https://docs.opslevel.com/docs/getting-started-with-custom-actions).
