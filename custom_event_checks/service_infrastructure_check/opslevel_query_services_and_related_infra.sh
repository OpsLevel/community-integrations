#!/bin/bash

# references the OpsLevel api token exported in the environment
API_TOKEN=$OPSLEVEL_API_TOKEN

OL_CEC_ENDPOINT="https://app.opslevel.com/integrations/custom_event/<ADD ENDPOINT TOKEN FROM OPSLEVEL HERE>"

# query services and related infrastructure
OL_SERVICES_AND_INFRA=$(opslevel graphql --api-token="$API_TOKEN" --paginate -a=".account.services.nodes[]" -q='query services_and_infra($endCursor:String){
  account{                                                               
    services(after: $endCursor){
      pageInfo{
        endCursor
        hasNextPage
      }
      nodes{
        name
        id
        aliases
        relatedResources{
          nodes{
            ... on InfrastructureResource{
              __typename
              name
              id
              type
              href
              rawData
            }
          }
        }
      }
    }
  }
}')

# select only services that have databases
OL_PAYLOAD=$(echo $OL_SERVICES_AND_INFRA | jq 'map(select(.relatedResources.nodes[] | .__typename == "InfrastructureResource" and .type == "Database")) | unique_by(.name)')

curl -i \
    -H "Content-Type: application/json" \
    -X POST "$OL_CEC_ENDPOINT" \
    --data-binary "$OL_PAYLOAD"