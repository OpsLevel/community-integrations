#!/bin/bash

# Fill in your API tokens/parameters:
CC_API_TOKEN="<ADD CC API TOKEN HERE>"
CC_ORG_ID="<ADD CODE CLIMATE ORG ID HERE>"
OL_CEC_ENDPOINT="https://app.opslevel.com/integrations/custom_event/<ADD ENDPOINT TOKEN FROM OPSLEVEL HERE>"

# Make sure each OpsLevel service has the human_name in Code Climate (aka GitHub's Repository name) as an Alias 
# (this assumes each OpsLevel service is tied to one repo and vice versa, at max)

CC_REPOS=$(curl \
  -H "Accept: application/vnd.api+json" \
  -H "Authorization: Token token=$CC_API_TOKEN" \
   https://api.codeclimate.com/v1/orgs/$CC_ORG_ID/repos)

for repo in $(echo "$CC_REPOS" | jq -r '.data[] | @base64');do

REPO_ID=$(echo "$repo" | base64 --decode | jq -r '.id');
REPO_NAME=$(echo "$repo" | base64 --decode | jq -r '.attributes.human_name');

TEST_COVERAGE_REPORTS=$(curl \
  -H "Accept: application/vnd.api+json" \
  -H "Authorization: Token token=${CC_API_TOKEN}" \
  --get \
  --data-urlencode "page[size]=1" \
  # page[size]=1 to get only the most recent result
  https://api.codeclimate.com/v1/repos/$REPO_ID/test_reports)

curl -i \
    -H "Content-Type: application/json" \
    -X POST "$OL_CEC_ENDPOINT"?service=$REPO_NAME \
    --data-binary "$TEST_COVERAGE_REPORTS"

done

# On OpsLevel side, define CEC to tie to the CEC Endpoint we're sending data to, "$params.service" for the Service Specifier
# Success condition to look for ".data[] | .attributes.rating.letter == "A"" 
# (depends on what you want to look for, if you want to check for another rating, change A to whatever)
# for testing, make sure to enter something like "service=<service_alias>" for "Sample Query Params"
