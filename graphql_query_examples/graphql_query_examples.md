## 🔎 Queries

### 🔎 GraphQL schema introspection query

```graphql
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args {
        ...InputValue
      }
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
```

### 🔎 campaigns > all

```graphql
query get_campaigns($endCursor: String){
  account{
    campaigns(after: $endCursor){
      nodes{
        id
        name
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}
```

### 🔎 campaign (query a specific campaign)

```graphql
query get_campaign_details{
   account{
       campaign(id:"Z2lkOi8vb3BzbGV2ZWwvQ2FtcGFpZ24vMTA2OA"){
           name
           owner{
               name
           }
           projectBrief
       }
   } 
}
```

### 🔎 checks (query for “everything”)

```graphql
query get_checks($endCursor: String) {
  account {
    rubric {
      checks(after: $endCursor) {
        nodes {
          id
          name
          type
          category {
            id
            name
          }
          description
          enabled
          enableOn
          filter {
            id
            name
          }
          level {
            id
            name
          }
          notes
          owner {
            ... on Team {
              name
            }
          }
          type
        }
        pageInfo{
          endCursor
          hasNextPage
        }
      }
    }
  }
}
```

### 🔎 check: RepositoryFileCheck (get details for a specific check), get checks first

```graphql
query get_checks_short_info($endCursor:String) {
  account {
    rubric {
      checks(after: $endCursor) {
        nodes {
          id
          name
          type
        }
        pageInfo{
          endCursor
          hasNextPage
        }
      }
    }
  }
}

query get_repo_file_check {
  account{
    check(id:"Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpSZXBvRmlsZS80Njcy"){
    name
      ...on RepositoryFileCheck{
        description
        filter {
          id
        }
        filePaths
        fileContentsPredicate {
          type
          value
        }
      }
    }
  }
}
```

### 🔎 deploys (for a specific service within a specific timerange)

```graphql
query deploys_just_for_shopping_cart($endCursor:String) {
  account {
    deploys(
      start: "2024-01-01T00:00:00.000Z"
      end: "2024-01-31T23:59:59.999Z"
      environments: ["production", "staging"]
      serviceId: {alias: "shopping_cart"}
      after: $endCursor
    ) {
      totalCount
      filteredCount
      nodes {
        id
        description
        environment
        service {
          id
          name
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "deploys": {
        "totalCount": 1078,
        "filteredCount": 199,
        "nodes": [
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRGVwbG95LzE0MzQ1OTAw",
            "description": "Updated Operations Center UI",
            "environment": "Production",
            "service": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQzMg",
              "name": "Shopping Cart Service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRGVwbG95LzE0MzQ2MzYw",
            "description": "Updated Operations Center UI",
            "environment": "Production",
            "service": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQzMg",
              "name": "Shopping Cart Service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRGVwbG95LzE0MzQ2NjA5",
            "description": "Updated Operations Center UI",
            "environment": "Staging",
            "service": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQzMg",
              "name": "Shopping Cart Service"
            }
          }
        ],
        "pageInfo": {
          "endCursor": "MTAw",
          "hasNextPage": true
        }
      }
    }
  }
}
```
</details>

### 🔎 filters

```graphql
query get_filters{
  account{
    filters{
      edges{
        node{
          name
          predicates {
            type
            key
            value
            keyData
          }
          id
          connective
          htmlUrl
        }
      }
    }
  }
}
```


### 🔎 infrastructureResources (get all)

```graphql
query get_all_infra_resources($endCursor: String) {
  account {
    infrastructureResources(after: $endCursor) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        id
        name
        href
        rawData
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "infrastructureResources": {
        "nodes": [
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxNjUzOQ",
            "name": "books-db",
            "href": "/catalog/infrastructures/216539"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwMg",
            "name": "gke-shopping-cart-prod-1",
            "href": "/catalog/infrastructures/212502"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwMw",
            "name": "gke-shopping-cart-prod-2",
            "href": "/catalog/infrastructures/212503"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwNA",
            "name": "gke-shopping-cart-staging-1",
            "href": "/catalog/infrastructures/212504"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwNQ",
            "name": "gke-shopping-cart-staging-2",
            "href": "/catalog/infrastructures/212505"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwNg",
            "name": "gke-catalog-service-prod-1",
            "href": "/catalog/infrastructures/212506"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwNw",
            "name": "gke-catalog-service-prod-2",
            "href": "/catalog/infrastructures/212507"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwOA",
            "name": "gke-catalog-service-staging-1",
            "href": "/catalog/infrastructures/212508"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjUwOQ",
            "name": "gke-catalog-service-staging-2",
            "href": "/catalog/infrastructures/212509"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMzExMQ",
            "name": "gke-author-pages-prod-1",
            "href": "/catalog/infrastructures/213111"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjg5NA",
            "name": "gcp-vpc-1",
            "href": "/catalog/infrastructures/212894"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjg5NQ",
            "name": "gcp-vpc-2",
            "href": "/catalog/infrastructures/212895"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjg5Ng",
            "name": "gcp-vpc-3",
            "href": "/catalog/infrastructures/212896"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMzExNA",
            "name": "gcp-vpc-5",
            "href": "/catalog/infrastructures/213114"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzQ1MTY2Mw",
            "name": "gcp-vpc-5",
            "href": "/catalog/infrastructures/451663"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzQ1MTY2NA",
            "name": "gcp-vpc-5",
            "href": "/catalog/infrastructures/451664"
          }
        ]
      }
    }
  }
}
```
</details>
    

### 🔎 infrastructureResourceSchemas

```graphql
query infrastructureResourceSchemas {
  account {
    infrastructureResourceSchemas {
      nodes {
        type
        schema
      }
    }
  }
}
```


### 🔎 integrations (get all)

```graphql
query integrations($endCursor: String){
  account{
    integrations(after: $endCursor){
      nodes{
        id
        name
        createdAt
        type
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "integrations": {
        "nodes": [
          {
            "node": {
                "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpBd3NJbnRlZ3JhdGlvbi8yOTM1",
                "name": "AWS - 694260482182",
                "type": "aws"
            }
          },
          {
            "node": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpFdmVudHM6OkRlcGxveUludGVncmF0aW9uLzExMDU",
              "name": "Deploy",
              "type": "deploy"
            }
          },
          {
            "node": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpFdmVudHM6OkdlbmVyaWNJbnRlZ3JhdGlvbnM6OlNueWtJbnRlZ3JhdGlvbi8xMzcz",
              "name": "Snyk",
              "type": "snyk"
            }
          },
          {
            "node": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpJc3N1ZVRyYWNraW5nOjpKaXJhU29mdHdhcmVJbnRlZ3JhdGlvbi8xNTA0",
              "name": "Jira Software",
              "type": "jiraSoftware"
            }
          },
          {
            "node": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpFdmVudHM6OkRvY3VtZW50czo6QXBpRG9jSW50ZWdyYXRpb24vMTk2OA",
              "name": "API Docs",
              "type": "apiDoc"
            }
          },
          {
            "node": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpTY2ltSW50ZWdyYXRpb24vMjEwNg",
              "name": "SCIM",
              "type": "scim"
            }
          },
          {
            "node": {
              "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpEYXRhZG9nSW50ZWdyYXRpb24vMTMzNA",
              "name": "Datadog",
              "type": "datadog"
            }
          }
        ],
        "pageInfo": {
          "endCursor": "Mzc",
          "hasNextPage": false
        }
      }
    }
  }
}
```
</details>

### 🔎 integrations (get by type)

types available: `github, bitbucket, gitlab, gitlabSelfManaged, sourceControl, slack, check, deploy, flux, payload, generic, monitoring, incidentNotifying, onCall, jira, api_doc, azure_devops, aws, aqua security, aws ecr, bugsnag, codacy, coveralls, datadog check, dynatrace, grafana, grype, jfrog xray, lacework, new relic check, prisma cloud, prometheus, rollbar, sentry, snyk, sonarqube, stackhawk, sumo logic, veracode`

#### example: AWS integrations

```graphql
query aws_integrations{
  account{
    integrations(type: "aws"){
      nodes{
        ... on AwsIntegration{
          name
          id
          externalId
          createdAt
          ownershipTagKeys
        }
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "integrations": {
        "nodes": [
          {
            "name": "AWS - 111111111111",
            "id": "J2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpBd3NJbnRlZ3JhdGlvbi8yNzUy",
            "externalId": "xxxxxxxx",
            "createdAt": "2023-03-24T15:35:22.421586Z",
            "ownershipTagKeys": [
              "owner"
            ]
          }
        ]
      }
    }
  }
}
```
</details>

#### example: GitLab integrations


```graphql
query gitlab_integrations{
  account{
    integrations(type: "gitlab"){
      nodes{
        ... on GitlabIntegration{
        name
        id
        displayName
        accountName
        active
        }
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "integrations": {
        "nodes": [
          {
            "name": "GitLab SaaS - ian roys test group",
            "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpHaXRsYWJJbnRlZ3JhdGlvbi8xNDQ4",
            "displayName": "GitLab SaaS",
            "accountName": "i3482",
            "active": true
          },
          {
            "name": "GitLab SaaS - GitLab SaaS",
            "id": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpHaXRsYWJJbnRlZ3JhdGlvbi8xNjg5",
            "displayName": "GitLab SaaS",
            "accountName": null,
            "active": false
          }
        ]
      }
    }
  }
}
```
</details>

### 🔎 payloads (for Custom Event Integrations), get integrations first

Note: This will return all CEC payloads for the specified integration in a single stream chronologically.

```graphql
query integrations($endCursor: String) {
  account {
    integrations(after: $endCursor) {
      nodes {
        id
        name
        createdAt
        type
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}

query payloads_for_custom_event_integration {
  account {
    payloads(
      sortBy: created_at_DESC
      first: 50
      filter: {key: integration_id, type: equals, arg: "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpTbGFja0ludGVncmF0aW9uLzEwNzM"}
    ) {
      nodes {
        data
      }
    }
  }
}
```

### 🔎 public IP Address

```graphql
query get_opslevel_public_ips {
  publicIpAddresses
}
```

### 🔎 repositories (get repository aliases and ids)

```graphql
query get_all_repository_aliases($endCursor: String) {
  account {
    repositories(after: $endCursor) {
      nodes {
        name
        defaultAlias
        id
        owner {
          id
          name
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
```

### 🔎 repositories (compare owner and ownerAlias to confirm valid owners)

When an owner alias is set in an opslevel.yml, it will be returned as `ownerAlias` in the API. If the `ownerAlias` is valid, the `owner` will also be set. If the `ownerAlias` is invalid, the `owner` will be null in the API.

```graphql
query repositories($endCursor: String){
  account{
    repositories(after: $endCursor){
      nodes{
        name
        owner{
          alias
        }
        ownerAlias
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}
```

<details>
  <summary>Usage with opslevel-cli expand to show</summary>

The opslevel-cli command below will return a list of repositories by name that have an `ownerAlias` set but does not have a valid `owner`.

```bash
opslevel graphql --paginate -a=".account.repositories.nodes[]" -q='query repositories($endCursor: String){
  account{
    repositories(after: $endCursor){
      nodes{
        name
        owner{
          alias
        }
        ownerAlias
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}' | jq '.[] | select(.ownerAlias != null and .owner == null) | .name'
```

</details>

### 🔎 rubric (categories and levels)

```graphql
query get_rubric_levels_and_categories{
  account{
    rubric{
      levels {
        edges {
          node {
            id
            name
            alias
          }
        }
      }
      categories {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  }
}
```

### 🔎 rubric (get all the checks)

```graphql
query get_checks{
  account{
    rubric{
      checks {
        edges {
          node {
            id
            name
            type
            category {
              id
              name
            }
            description
            enabled
            enableOn
            filter {
              id
              name
            }
            level {
              id
              name
            }
            notes
            owner
            type
          }
        }
      }
    }
  }
}
```

### 🔎 services > all

```graphql
query get_services($endCursor: String) {
  account {
    services(after: $endCursor) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        name
        id
        aliases
        timestamps {
          createdAt
          updatedAt
        }
        owner {
          name
          alias
          id
        }
        language
        framework
        lifecycle {
          name
        }
        tier {
          name
        }
        parent {
          name
          __typename
          parent {
            name
            __typename
          }
        }
        product
        properties {
          nodes {
            definition {
              name
            }
            value
          }
        }
        tags {
          nodes {
            key
            value
            id
          }
        }
      }
    }
  }
}
```

### 🔎 services > query by filter (get filters first)

```graphql
query filters($endCursor: String) {
  account {
    filters(after: $endCursor) {
      nodes {
        name
        id
        connective
        predicates {
          keyData
          value
        }
        htmlUrl
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}

query services_by_filter($endCursor: String) {
  account {
    services(
      filterIdentifier: {id: "Z2lkOi8vb3BzbGV2ZWwvRmlsdGVyLzIwNjg"}
      after: $endCursor
    ) {
      nodes {
        name
        id
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}
```

### 🔎 services > query by tag

```graphql
query services_by_tag($endCursor: String) {
  account {
    services(
      tag: {key: "is_locked_by_opslevelyml", value: "true"}
      after: $endCursor
    ) {
      nodes {
        name
        id
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
```

### 🔎 services > query for all opslevel.yml config errors

```graphql
query get_all_service_opslevelyml_configErrors($endCursor: String){
  account{
    services(after: $endCursor){
      nodes{
        name
        locked
        configErrors{
          message
          sourceFilename
        }
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "services": {
        "nodes": [
          {
            "name": "Catalog Service",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Fraud Detection Service",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Internal Employee Directory",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Order Visualization Dashboard",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Order Workflow Service",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Payment Service",
            "locked": true,
            "configErrors": []
          },
          {
            "name": "Picking and Packing Service",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Procurement Service",
            "locked": true,
            "configErrors": [
              {
                "message": "Some errors occurred while adding dependencies from opslevel.yml.\n - 'sahara_dessert_services' does not identify a service on this account",
                "sourceFilename": "opslevel.yml"
              }
            ]
          },
          {
            "name": "Product Search",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Recommender 2.0",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Shopping Cart Service",
            "locked": false,
            "configErrors": null
          },
          {
            "name": "Support Console",
            "locked": true,
            "configErrors": []
          },
          {
            "name": "Warehouse Management Service",
            "locked": false,
            "configErrors": null
          }
        ],
        "pageInfo": {
          "endCursor": "Njk",
          "hasNextPage": false
        }
      }
    }
  }
}
```
</details>

### 🔎 services > maturityReport > overallLevel (for all services)

```graphql
query services_overallLevel_for_all($endCursor: String) {
  account {
    services(after: $endCursor) {
      nodes {
        id
        maturityReport {
          overallLevel {
            id
            name
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
```

### 🔎 services > maturityReport > latestCheckResults (show results for a check and all matching services)

```graphql
query get_checks_id_and_name($endCursor: String) {
  account {
    rubric {
      checks(after: $endCursor) {
        nodes {
          id
          name
        }
      }
    }
  }
}

query get_results_for_list_of_checks($endCursor: String) {
  account {
    services(after: $endCursor) {
      nodes {
        maturityReport {
          latestCheckResults(ids: ["Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpIYXNPd25lci8zNjQz"]) {
            check {
              id
            }
            service {
              id
            }
            serviceAlias
            status
            message
          }
        }
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
        "services": {
        "nodes": [
            {
            "maturityReport": {
                "latestCheckResults": [
                {
                    "check": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpSZXBvRmlsZS8zNjQy"
                    },
                    "service": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQyMw"
                    },
                    "serviceAlias": "catalog_service",
                    "status": "passed",
                    "message": "Repo file <a href='https://github.com/gandalfsbooks/scala-monorepo/blob/2.5/catalog-service/build.sbt' target='_blank'>build.sbt</a> contains ' akkaVersion = \"2.5'."
                }
                ]
            }
            },
            {
            "maturityReport": {
                "latestCheckResults": [
                {
                    "check": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpSZXBvRmlsZS8zNjQy"
                    },
                    "service": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQyNA"
                    },
                    "serviceAlias": "fraud_detection_service",
                    "status": "passed",
                    "message": "Repo file <a href='https://github.com/gandalfsbooks/scala-monorepo/blob/2.5/fraud-service/build.sbt' target='_blank'>build.sbt</a> contains ' akkaVersion = \"2.5'."
                }
                ]
            }
            },
            {
            "maturityReport": {
                "latestCheckResults": [
                {
                    "check": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpSZXBvRmlsZS8zNjQy"
                    },
                    "service": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQyNw"
                    },
                    "serviceAlias": "order_workflow_service",
                    "status": "passed",
                    "message": "Repo file <a href='https://github.com/gandalfsbooks/scala-monorepo/blob/2.5/order-workflow-service/build.sbt' target='_blank'>build.sbt</a> contains ' akkaVersion = \"2.5'."
                }
                ]
            }
            }
        ]
        }
    }
    }
}
```
</details>

### 🔎 services > query for all services with openapi docs

If an OpenAPI doc is found for a service, `preferredApiDocument.content` 
field will be set. Otherwise `preferredApiDocument.content` will be null.

```graphql
query all_services_with_openapi_docs($endCursor: String) {
  account {
    services(after: $endCursor) {
      nodes {
        name
        preferredApiDocument {
          content
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
```

<details>
  <summary>Usage with opslevel-cli expand to show</summary>
The opslevel-cli command below will return a list of services by name that have `preferredApiDocumentSource` set.

```bash
opslevel graphql --paginate -a=".account.services.nodes[]" -q='query all_services_with_openapi_docs($endCursor: String) {
  account {
    services(after: $endCursor) {
      nodes {
        name
        preferredApiDocument {
          content
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}' | jq '.[] | select(.preferredApiDocument.content != null) | .name'
```
</details>

### 🔎 service (query for ”everything” for a specific service)

```graphql
query get_service_info_long{
  account{
    service(alias: "support_console"){
      id
      name
      aliases
      timestamps{
        createdAt
        updatedAt
      }
      owner {
        id
        alias
      }
      maturityReport{
        overallLevel {
          id
        }
        categoryBreakdown{
          level{
            id
            name
          }
          category{
            id
            name
          }
        }
      }
      tools{
        nodes{
          id
          displayName
          category
        }
      }
      tags{
        edges{
          node{
            id
            owner
            key
            value
          }
        }
      }
      repos{
        edges {
          node {
            id
          }
          serviceRepositories {
            id
            baseDirectory
          }
        }
      }
    }
  }
}
```

### 🔎 service > alertSources (get alertsource ids for a specific service)

```graphql
query alertsource_info{
  account {
    service(alias: "shopping_cart_service") {
      id
      name
      alertSources{
        nodes{
          name
          externalId
          type
        }
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "service": {
        "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQzMg",
        "name": "Shopping Cart Service",
        "alertSources": {
          "nodes": [
            {
              "name": "Shopping Cart Service",
              "externalId": "PHHMSFUV",
              "type": "pagerduty"
            },
            {
              "name": "[Demo] - Gandalf's CPU Usage is High",
              "externalId": "657066391",
              "type": "datadog"
            },
            {
              "name": "[Demo] - Green monitor",
              "externalId": "489984512",
              "type": "datadog"
            }
          ]
        }
      }
    }
  }
}
```
</details>

### 🔎 service > checkStats (get check status for a specific service)

```graphql
query get_checkstats_for_a_service{
 account{
    service(alias: "support_console"){
      name
      aliases
      checkStats{
        totalChecks
        totalPassingChecks
      }
    }
  }
}
```

### 🔎 service > dependencies and dependents (get linked dependencies for a specific service)

```graphql
query get_service_dependencies_and_dependents{
  account{
    service(alias: "shopping_cart"){
      name
      dependencies{
        edges{
          node{
            name
          }
          notes
        }
      }
      dependents{
        edges{
          node{
            name
          }
          notes
        }
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "service": {
        "name": "Shopping Cart Service",
        "dependencies": {
          "edges": [
            {
              "node": {
                "name": "Catalog Service"
              },
              "notes": "Disable rate-limiting in Catalog Service for Shopping Cart Service.\n\nDone!"
            },
            {
              "node": {
                "name": "Order Workflow Service"
              },
              "notes": null
            },
            {
              "node": {
                "name": "Product Image Service"
              },
              "notes": null
            },
            {
              "node": {
                "name": "Recommender 2.0"
              },
              "notes": "GraphQL api schema for Recommender 2.0 still in alpha and under development. Target Completion date: Q4-2022.\n\nDone!"
            }
          ]
        },
        "dependents": {
          "edges": [
            {
              "node": {
                "name": "Website Aggregator"
              },
              "notes": "Move to using the GraphQL API in Q4"
            }
          ]
        }
      }
    }
  }
}
```
</details>

### 🔎 service > documents (get documents for a specific service), get services first

```graphql
query get_services($endCursor: String){
  account{
    services(after: $endCursor){
      nodes{
        name
        id
        aliases
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}

query get_api_docs{
  account{
    service(alias: "shopping_cart"){
      documents{
        nodes{
          content
        }
      }
    }
  }
}
```

### 🔎 service > maturityReport > overallLevel (get overall level for a specific service)

```graphql
query get_level{
  account{
    service(alias: "support_console"){
      maturityReport{
        overallLevel {
          id
          name
        }
      }
      name
      aliases
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "service": {
        "maturityReport": {
            "overallLevel": {
            "id": "Z2lkOi8vb3BzbGV2ZWwvTGV2ZWwvNjc1",
            "name": "Bronze"
            }
        },
        "name": "Support Console GitHub",
        "aliases": [
            "support_console",
            "support_console_github",
            "Support Console"
        ]
        }
    }
    }
}
```
</details>

### 🔎 service > owner > contacts info (owner and contact info for a specific service)

```graphql
query get_service_and_owner_contact_info{
  account{
    service(alias: "support_console"){
      name
      id
      aliases
      owner {
        id
        alias
        name
        contacts {
          address
          displayName
          id
          type
        }
      }
    }
  }
}
```

### 🔎 service > maturityReport > latestCheckResults (for a list of checks for a specific service)

```graphql
query get_check_results_for_a_service{
  account{
    service(alias: "support_console"){
      owner {
        id
        alias
      }
      maturityReport{
        overallLevel {
          id
        }
        latestCheckResults(ids: ["Z2lkOi8vb3BzbGV2ZWwvQ2hlY2tzOjpIYXNPd25lci8zMTU5"] ) {
          serviceAlias
          check {
            id
          }
          status
        }
      }
    }
  }
}
```

### 🔎 systems (get all)

```graphql
query get_all_systems($endCursor: String) {
  account {
    systems(after: $endCursor) {
      nodes {
        id
        name
        description
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "systems": {
        "nodes": [
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzQ4",
            "name": "Non-Customer Facing",
            "description": "Internal Services and Tools"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzUw",
            "name": "Social",
            "description": "Services supporting user actions and subscriptions"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzUx",
            "name": "Promotions",
            "description": "Marketing and promotional services and infrastructure"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzUy",
            "name": "Recommendations",
            "description": "Personalized recommendation related applications"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzUz",
            "name": "Support",
            "description": "Customer support related application services"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzU0",
            "name": "Catalog",
            "description": "Serves up items for purchase in-app"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzU1",
            "name": "Cart",
            "description": "Manages how items are managed during the purchase process"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzU2",
            "name": "Orders",
            "description": "Serves up functionality from order placement to fulfillment"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzU4",
            "name": "Website",
            "description": "Publicly-available web experience"
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzYw",
            "name": "Platform",
            "description": "Internal tooling for use by developers"
          }
        ],
        "pageInfo": {
          "endCursor": "NA",
          "hasNextPage": false
        }
      }
    }
  }
}
```
</details>

### 🔎 teams (get all teams)

```graphql
query get_all_teams($endCursor: String) {
  account {
    teams(after: $endCursor) {
      nodes {
        id
        alias
        aliases
        contacts {
          type
          displayName
          address
        }
        memberships {
          nodes {
            user {
              id
              name
              email
            }
            role
          }
        }
        responsibilities
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}
```

### 🔎 team > parentTeam info

```graphql
query get_team{
  account{
    team(alias: "devx"){
      id
      name
      parentTeam{
        name
        alias
      }
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "account": {
      "team": {
        "id": "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8zMTE0",
        "name": "DevX",
        "parentTeam": {
          "name": "Engineering",
          "alias": "engineering"
        }
      }
    }
  }
}
```
</details>

### 🔎 tiers and lifecycles (service tiers and lifecycles)

```graphql
query get_service_tiers_and_lifecycles{
  account{
    tiers {
      id
      name
      alias
    }
    lifecycles{
      id
      name
      alias
    }
  }
}
```

### 🔎 users (get all users)

```graphql
query get_users($endCursor: String) {
  account {
    users(after: $endCursor) {
      nodes {
        id
        email
      }
    }
  }
}
```

### 🔎 users (get all active users only)

```graphql
query users_active_only{
  account {
    users(filter: [{ key: deactivated_at, arg: null, type: equals }]) {
      nodes {
        id
        name
        email
      }
    }
  }
}
```
