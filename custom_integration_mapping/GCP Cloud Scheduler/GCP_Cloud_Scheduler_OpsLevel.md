# Google Cloud Scheduler to OpsLevel Integration Guide

## Overview

Integrate Google Cloud Scheduler jobs with OpsLevel as custom components using OpsLevel's custom integration webhook. This allows automatic tracking and management of your GCP Cloud Scheduler jobs within OpsLevel.

## Quick Start Architecture

```
GCP Projects → Fetch with gcloud CLI → Transform to JSON → OpsLevel Webhook → Components
```

## Prerequisites

- **OpsLevel Permissions**: Account with custom integration permissions.
- **OpsLevel Custom Component Type**: Create your own Component Type with name like "Cloud Scheduled Jobs", and define custom properties like Location, Name, Project ID, State etc.
- **GCP**: Projects with Cloud Scheduler API enabled, IAM permission `cloudscheduler.jobs.list`
- **Tools**: gcloud CLI, jq, curl
- **Auth**: Authenticated gcloud session

## Step 1: Create OpsLevel Custom Integration

1. Navigate to **Integrations** → **Custom Integrations** → **Create Custom Integration**
2. Configure:
   - **Name**: `GCP Cloud Scheduler Integration`
   - **Integration Type**: Webhook
   - **External Kind**: `gcp_cloud_scheduler`
3. Save and copy the webhook URL:
   ```
   https://app.opslevel.com/integrations/custom/webhook/{unique-id}
   ```

## Step 2: Configure Extract and Transform

### Extract Definition

The extract configuration tells OpsLevel how to parse incoming webhook data:

```yaml
---
extractors:
  - external_kind: gcp_cloud_scheduler
    iterator: ".data"
    external_id: ".name"
```

**Syntax Explanation**:
- `extractors:` - Root array containing extraction rules
- `external_kind:` - Matches the identifier sent in webhook payload
- `iterator:` - JSONPath expression to the array of objects (`.data` means iterate over the `data` field)
- `external_id:` - JSONPath to unique identifier for each component (`.name` extracts the `name` field)

### Transform Definition

The transform configuration maps GCP data to OpsLevel component properties:

```yaml
---
transforms:
  - external_kind: gcp_cloud_scheduler
    on_component_not_found: Create
    opslevel_kind: cloud_scheduled_jobs
    opslevel_identifier: ".name"
    properties:
      name: .name | split("/")[-1] | tostring # (To extract part of string)
      state: ".state"
      location: .name | split("/")[3] | tostring
```

**Syntax Explanation**:

- `transforms:` - Root array containing transformation rules
- `external_kind:` - Matches the external kind from extract definition
- `on_component_not_found:` - Action when component doesn't exist (`Create` or `Ignore`)
- `opslevel_kind:` - Custom component type name in OpsLevel
- `opslevel_identifier:` - JSONPath to create unique OpsLevel component alias
- `properties:` - Key-value mappings for component properties

**JSONPath Transformation Syntax**:
- `.fieldname` - Direct field access
- `|` - Pipe operator to chain operations
- `split("/")` - Split string by delimiter
- `[1]` - Access array element by index
- `[-1]` - Access last array element
- `split("-")[0]` - Split and get first element
- `tostring` - Convert to string type

**Example Transformation**:
```
Input: "projects/my-project-id/locations/us-central1/jobs/my-scheduler-job"

project_id: ... → split("/") → [1] → "my-project-id"

name: ... → split("/") → [-1] → "my-scheduler-job"

location: ... → split("/") → [3] → "us-central1"

state: Direct extraction of .state field value
```

## Step 3: Authenticate with GCP

```bash
# Install and authenticate
gcloud auth login

# Verify access
gcloud scheduler jobs list \
  --project=YOUR_PROJECT_ID \
  --location=YOUR_LOCATION \
  --format=json
```

## Step 4: Collect Cloud Scheduler Data

### Query Single Project
```bash
gcloud scheduler jobs list \
  --project=YOUR_PROJECT_ID \
  --location=YOUR_LOCATION \
  --format="json(name, description, schedule, state, timeZone, lastAttemptTime, status, topicName)"
```

### Query Multiple Projects
Iterate through all projects and locations, merging results into a single array.

**Key Fields**:
- `name` - Full resource path (unique identifier)
- `description` - Job description
- `schedule` - Cron expression or schedule descriptor
- `state` - ENABLED, PAUSED, or DISABLED
- `timeZone` - IANA timezone identifier
- `lastAttemptTime` - ISO 8601 timestamp
- `topicName` - Pub/Sub topic (if applicable)

## Step 5: Send to OpsLevel Webhook

### Required Payload Format

The gcloud command returns an array of Cloud Scheduler jobs. This array must be wrapped in an object with two fields:
- `external_kind`: Identifier matching your OpsLevel integration configuration
- `data`: The array of jobs from gcloud command

```json
{
  "external_kind": "gcp_cloud_scheduler",
  "data": [
    {
      "name": "projects/my-project/locations/us-central1/jobs/daily-job",
      "description": "Daily processing job",
      "schedule": "0 2 * * *",
      "state": "ENABLED",
      "timeZone": "America/New_York",
      "lastAttemptTime": "2025-11-04T02:00:00.000Z",
      "topicName": "projects/my-project/topics/my-topic",
      "status": {}
    }
  ]
}
```

**Important**: The `gcloud scheduler jobs list` command returns a JSON array. You must wrap this array as the value of the `data` field before sending to the webhook.

```json
{
  "external_kind": "gcp_cloud_scheduler",
  "data": [/* your array of jobs here */]
}
```

### Send with curl
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @payload.json \
  YOUR_WEBHOOK_URL
```

**Success Codes**: 200, 201, 202, 204

## Complete Implementation Example

### Bash Script
```bash
#!/bin/bash
set -euo pipefail

# Configuration
WEBHOOK_URL="YOUR_WEBHOOK_URL"
PROJECTS=("project-a" "project-b")
LOCATIONS=("us-central1" "europe-west1")

# Initialize results
echo "[]" > jobs.json

# Collect jobs from all projects/locations
for project in "${PROJECTS[@]}"; do
    for location in "${LOCATIONS[@]}"; do
        echo "Querying ${project} in ${location}..."
        
        result=$(gcloud scheduler jobs list \
            --project="${project}" \
            --location="${location}" \
            --format="json(name, description, schedule, state, timeZone, lastAttemptTime, topicName, status)" \
            2>/dev/null || echo "[]")
        
        # Merge results
        jq -s '.[0] + .[1]' jobs.json <(echo "$result") > jobs.tmp
        mv jobs.tmp jobs.json
    done
done

# Count total jobs
TOTAL=$(jq 'length' jobs.json)
echo "Total jobs found: ${TOTAL}"

# Wrap for OpsLevel
jq '{"external_kind": "gcp_cloud_scheduler", "data": .}' jobs.json > payload.json

# Send to webhook
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d @payload.json \
    "$WEBHOOK_URL")

# Check response
if [[ "$HTTP_CODE" =~ ^(200|201|202|204)$ ]]; then
    echo "✓ Successfully synced to OpsLevel (HTTP ${HTTP_CODE})"
    exit 0
else
    echo "✗ Failed to sync (HTTP ${HTTP_CODE})"
    exit 1
fi
```

## Schedule Automated Syncs To Ensure Data Freshness

### Using Cron (Linux/Unix)
```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * /path/to/sync-script.sh >> /var/log/scheduler-sync.log 2>&1
```

### Using Cloud Scheduler
Create a Cloud Scheduler job that triggers a Cloud Function or Cloud Run service containing your sync script.


## Troubleshooting

| Issue | Solution |
|-------|----------|
| No jobs found | Enable Cloud Scheduler API, verify project ID and location |
| Authentication error | Run `gcloud auth login` and verify permissions |
| 400 Bad Request | Validate JSON structure and `external_kind` value |
| Components not appearing | Check OpsLevel integration logs and field mappings |
| Duplicate components | Ensure `external_id` is unique (use full resource path) |

## Best Practices

**Security**:
- Store webhook URL in environment variables or secrets manager
- Use service accounts with minimal permissions (`cloudscheduler.jobs.list`)
- Never commit credentials to version control

**Reliability**:
- Implement retry logic with exponential backoff
- Handle project access errors gracefully (skip and continue)
- Log all operations with timestamps
- Monitor sync success/failure rates

**Data Quality**:
- Query all relevant GCP regions
- Validate JSON before sending
- Include comprehensive metadata
- Handle empty results (send empty array)

## Customization Examples

### Filter Only Enabled Jobs
```bash
gcloud scheduler jobs list --filter="state=ENABLED" ...
```

### Add Custom Properties
```python
for job in all_jobs:
    job['environment'] = 'production' if 'prod' in job['name'] else 'non-production'
    job['managed_by'] = 'devops'
```

### Extract Additional Fields from Name
```yaml
properties:
  client: .name | split("/")[1] | split("-")[0] | tostring
  environment: .name | split("/")[1] | split("-")[-1] | tostring
  region: .name | split("/")[3] | tostring
  job_name: .name | split("/")[-1] | tostring
```

## Verification Steps

1. Send test payload to webhook
2. Navigate to **Components** in OpsLevel
3. Filter by `cloud_scheduled_jobs` kind (or your custom kind)
4. Verify components were created with correct properties
5. Check that aliases are unique and formatted correctly
6. Validate property values extracted properly

## Advanced Configuration

### Complex Property Transformations

For more complex data extraction, use advanced JSONPath operations:

```yaml
properties:
  # Conditional transformations
  is_production: .name | contains("prod") | tostring
  
  # Multiple splits and array access
  account_name: .name | split("/")[1] | split("-")[0:-1] | join("-")
  
  # Direct field mapping
  schedule_expression: ".schedule"
  current_state: ".state"
  timezone: ".timeZone"
  
  # Nested field access
  last_attempt: ".lastAttemptTime"
  target_topic: ".topicName"
```

### Multiple External Kinds

If you have different types of schedulers:

```yaml
---
extractors:
  - external_kind: gcp_cloud_scheduler_production
    iterator: ".data"
    external_id: ".name"
  - external_kind: gcp_cloud_scheduler_development
    iterator: ".data"
    external_id: ".name"

---
transforms:
  - external_kind: gcp_cloud_scheduler_production
    opslevel_kind: production_schedulers
    # ... properties
  - external_kind: gcp_cloud_scheduler_development
    opslevel_kind: development_schedulers
    # ... properties
```

## Resources

- **OpsLevel**: Custom Integrations Documentation
- **GCP**: Cloud Scheduler API Reference
- **Tools**: gcloud CLI, jq manual, JSONPath documentation

---

**Version**: 1.0
**Last Updated**: November 2025

