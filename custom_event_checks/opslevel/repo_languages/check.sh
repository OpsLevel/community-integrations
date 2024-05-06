#!/usr/bin/env bash

OPSLEVEL_API_TOKEN="<ADD CC API TOKEN HERE>"
OL_CEC_ENDPOINT="https://app.opslevel.com/integrations/custom_event/<ADD ENDPOINT TOKEN FROM OPSLEVEL HERE>"

DATA=$(opslevel graphql --paginate -q='
query ($endCursor: String){
  account {
    services(after: $endCursor) {
      nodes {
        alias
        repos {
          nodes {
            languages {
              name
              usage
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
')

PAYLOAD=$(echo $DATA | jq '.[0].account.services.nodes | map({"alias": (.alias), "languages": ((.repos.nodes | length) as $count | .repos.nodes | map(.languages[]) | map({(.name):(.usage / $count)}) | add)})')

curl -i \
    -H 'content-type: application/json' \
    -X POST ${OL_CEC_ENDPOINT} \
    --data-binary $PAYLOAD