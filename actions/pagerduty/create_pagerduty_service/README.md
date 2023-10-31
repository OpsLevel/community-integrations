# Build an Action used to create a new Service in Pagerduty.

We're using this PagerDuty API call `POST https://api.pagerduty.com/services` to create the Service. The two JSON files show the JSON response from our GraphQL API for both parts of the Action config. I'll paste three of the fields below so they are easier to read and easy to copy+paste into the OpsLevel GUI.

The form submission details / customActionsTriggerDefinition.manualInputsDefinition is in YAML format:

```
version: 1
inputs:
  - identifier: escalation
    displayName: Escalation Policy
    type: dropdown
    values:
    - value: PQVP7JC
      display: OpsLevel
    - value: P3F54ZV
      display: Platform
    - value: PID26HM 
      display: Security
    required: true
```

The payload / customActionsExternalAction.liquidTemplate uses Liquid syntax:

```
{
	"service": {
		"type": "service",
		"name": "{{ service.name }}",
		"description": "Provisioned from OpsLevel: https://app.opslevel.com{{ service.href }}",
		"auto_resolve_timeout": null,
		"acknowledgement_timeout": null,
		"status": "active",
		"escalation_policy": {
			"id": "{{ manualInputs.escalation }}",
			"type": "escalation_policy_reference"
		},
		"incident_urgency_rule": {
			"type": "constant",
			"urgency":"high"
		},
		"alert_creation": "create_alerts_and_incidents",
		"alert_grouping_parameters": {
			"type": null
		}
	},
	"auto_pause_notifications_parameters": {
		"enabled": false
	}
}
```

The response message / customActionsTriggerDefinition.responseTemplate uses Liquid syntax:

```
{% if response.status >= 200 and response.status < 300 %}
## Congratulations!
Your request for {{ service.name }} has succeeded. Check it out [here]({{ response.body.service.html_url }})
{% else %}
## Oops something went wrong
Please contact [{{ action_owner.name }}]({{ action_owner.href }}) for more help.
{% endif %}
```


More information on creating Actions can be found [in our documentation](https://docs.opslevel.com/docs/getting-started-with-custom-actions).
