#!/bin/sh
# Fill in your API tokens or add these as secrets:
#ORG_GITLAB_TOKEN="ADD GITLAB API TOKEN HERE"
#ORG_GITHUB_TOKEN="ADD GITHUB API TOKEN HERE"
#OPSLEVEL_INTEGRATION_URL="https://app.opslevel.com/integrations/custom_event/<ADD ENDPOINT TOKEN FROM OPSLEVEL HERE>"

echo "${ORG_GITLAB_TOKEN}" | glab auth login --stdin
echo "${ORG_GITHUB_TOKEN}" | gh auth login --with-token

query_gitlab() {
    export ALIAS=${1}
    PROJECT=${2}
    QUERY=$(echo "query GetMRs{project(fullPath: \"${PROJECT}\") {mergeRequests(labels: [\"dependencies\"], state: opened) {nodes {webUrl title createdAt}}}}")
    DATA=$(glab api graphql --paginate -f query="${QUERY}" | jq '{alias: env.ALIAS, open: .data.project.mergeRequests.nodes | map({url: .webUrl, title: .title, age: ((now - (.createdAt | fromdateiso8601)) / 60 / 60 / 24 | round)})}')
    echo "[opslevel] checking project ${PROJECT}"
    echo $DATA
    echo $DATA | curl -s -X POST ${OPSLEVEL_INTEGRATION_URL} -H 'content-type: application/json'  --data-binary @-
    echo ""
}

query_github() {
    export ALIAS=${1}
    PROJECT=${2}
    OWNER="GITHUB_OWNER"
    QUERY=$(echo "query GetPRs{repository(owner: \"${OWNER}\", name: \"${PROJECT}\"){pullRequests(labels: [\"dependencies\"], states: OPEN, first: 100) { nodes { url title createdAt }}}}")
    DATA=$(gh api graphql -f query="${QUERY}" | jq '{alias: env.ALIAS, open: .data.repository.pullRequests.nodes | map({url: .url, title: .title, age: ((now - (.createdAt | fromdateiso8601)) / 60 / 60 / 24 | round)})}')
    echo "[opslevel] checking project ${OWNER}/${PROJECT}"
    echo $DATA
    echo $DATA | curl -s -X POST ${OPSLEVEL_INTEGRATION_URL} -H 'content-type: application/json'  --data-binary @-
    echo ""
}

echo "[opslevel] Checking Gitlab repos..."
query_gitlab "OPSLEVEL_SERVICE_ALIAS" "GITLAB_PROJECT_PATH"

echo "[opslevel] Checking Github repos..."
query_github "OPSLEVEL_SERVICE_ALIAS" "GITHUB_PROJECT_PATH"