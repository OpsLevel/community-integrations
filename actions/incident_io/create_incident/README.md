# OpsLevel Action for incident.io Incident Creation

This guide provides instructions on how to build a Custom Action in OpsLevel to create a new incident in incident.io. This allows users to declare incidents directly from the service catalog in OpsLevel, streamlining the incident response process.

We will use the incident.io `POST /v2/incidents` API endpoint to create the incident. This example is modeled after a similar action for creating PagerDuty incidents.

For more information on creating OpsLevel Actions, refer to the [official documentation](https://docs.opslevel.com/docs/getting-started-with-custom-actions).

## Prerequisites

Before you begin, ensure you have:
*   **Admin access** to your OpsLevel account to create and manage Custom Actions.
*   An **API key** from incident.io for authentication. Please refer to the [incident.io documentation](https://docs.incident.io/docs/api/making-requests/authentication) on how to generate one.
*   The **Severity IDs** from your incident.io account that you wish to use. These can be found via the incident.io API. The example payload includes placeholder IDs.

## 1. Configure the Action in OpsLevel

An OpsLevel Action consists of several parts: defining the user input form, configuring the HTTP request (URL, headers, and payload), and setting a response message to provide feedback to the user.

### Manual Inputs (The Form)

This YAML configuration defines the form a user will fill out when triggering the action. It includes fields for a description, severity, and incident mode. Remember to use 

```yaml
---
version: 1
inputs:
- identifier: description
  displayName: Description
  description: Description of the incident.
  type: text_area
  required: true
- identifier: severity
  displayName: Severity
  type: dropdown
  required: true
  defaultValue: Severity:3
  values: [Severity:1, Severity:2, Severity:3]
- identifier: mode
  displayName: Mode (Use test if it is not an active incident)
  type: dropdown
  required: true
  defaultValue: test
  values: [standard, retrospective, test, tutorial]
```

### HTTP Request Configuration

This section defines the HTTP request that OpsLevel sends to the incident.io API when the action is triggered.

#### Webhook URL
Set the URL to the incident.io API endpoint for creating incidents:
```
https://api.incident.io/v2/incidents
```

#### Headers
The headers must include `Content-Type`, and an `Authorization` token for the incident.io API. Use OpsLevel's secrets management to securely store your API key.

For more details on using secrets, see the [OpsLevel documentation on Secrets](https://docs.opslevel.com/docs/secrets).

```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{ '' | secret: 'incident-io-api-key' }}"
}
```
*Note: You will need to create a secret in OpsLevel with the alias `incident-io-api-key` containing your incident.io API token.*

#### Body (Payload)

The body of the request is a JSON payload constructed using [Liquid syntax](https://shopify.github.io/liquid/) to dynamically insert values from the manual inputs.

*   The `idempotency_key` helps prevent duplicate incidents from being created.
*   `name` and `mode` are taken directly from the user's form inputs.
*   The `severity_id` is mapped from the user-friendly severity name to the specific ID required by the incident.io API. **You must replace the placeholder IDs (`01HW5...`) with the actual IDs from your incident.io account**.
*   `visibility` is set to `public` by default.

```json
{
  "idempotency_key": "{{ "now" | date: "%s" }}",
  "mode": "{{ manualInputs.mode }}",
  "name": "{{ manualInputs.description }}",
  "severity_id": "{% if manualInputs.severity == 'Severity:3' %}01HW5KHDVN06RHHF77WN7{% elsif manualInputs.severity == 'Severity:2' %}01HW5KHDVN64AQVQ9T57{% elsif manualInputs.severity == 'Severity:1' %}01HVN7P7K1YZ7EQBFRCE7{% endif %}",
  "visibility": "public"
}
```

## 2. Configure the Response Message

The response message provides immediate feedback to the user after the action is triggered. It uses Liquid to conditionally display a success or failure message based on the HTTP status code of the API response.

For successful requests (HTTP status 200-299), it includes a direct link to the newly created incident in incident.io by accessing the `permalink` from the response body.

```liquid
{% if response.status >= 200 and response.status < 300 %}
You successfully created an incident for {{ service.name }}. See the incident [here]({{response.body.incident.permalink}}).
{% else %}
## Oops something went wrong
Please contact [{{ action_owner.name }}]({{ action_owner.href }}) for more help.
{% endif %}
```

## 3. Publish the Action

Once you have configured all the sections, the final step is to publish the action to make it available to users in your organization.

1.  Use the toggle at the bottom of the action configuration page to publish it.
2.  Optionally, you can use [OpsLevel Filters](https://docs.opslevel.com/docs/checks-and-filters) to control which services the action is available for, for example, by team, tier, or technology.