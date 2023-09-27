## 🧬 Mutations

### 🧬 aliasCreate, get service ids first

Use case: Add aliases to services in bulk with our API

```graphql
query get_services{
  account{
    services{
      nodes{
        name
        id
        aliases
      }
    }
  }
}

mutation aliasCreate_for_a_service{
  aliasCreate(input:{ownerId: "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80ODM2NQ", alias: "another_alias"}) {
    ownerId
    errors{
      message
      path
    }
  }
}
```

### 🧬 deployDelete, get deploy ids first

Use case: Delete a deploy that was sent as part of testing / POC. Delete a deploy with an environment that is no longer desired.

```graphql
query deploys_by_id_for_a_specific_service{
  account{
    deploys(start: "2022-12-15T00:00:00.000Z", end: "2022-12-15T23:59:59.999Z", serviceId:{alias: "shopping_cart"} ) {
      edges {
        node {
          id
          description
          environment
          service {
            name
          }
        }
      }
    }
  }
}

mutation delete_deploy_by_ids{
  deployDelete(input:{id: "Z2lkOi8vb3BzbGV2ZWwvRGVwbG95LzY0NDkyMTQ"}){
    deletedId
    errors{
      message
      path
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "deployDelete": {
        "deletedId": "Z2lkOi8vb3BzbGV2ZWwvRGVwbG95LzY0NDkyMTQ",
        "errors": []
    }
  }
}
```
</details>

### 🧬 externalUuidCreate (Service Level Maturity Badges), get service ids first

```graphql
query get_services{
  account{
    services{
      nodes{
        name
        id
        aliases
      }
    }
  }
}

mutation enable_badge_for_service{
  externalUuidCreate(input: {resourceId: "AZ2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzY3MA"}){
    externalUuid
    errors{
      message
      path
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "externalUuidCreate": {
        "externalUuid": "2UNlAY7LRcHe8F1ShKUyDjM-IgxUPnSr-XZ8v62ak7o",
        "errors": []
    }
  }
}
```
</details>

### 🧬 groupCreate (parent group, top level group)

```graphql
mutation create_Group_for_me_1{
  groupCreate(input: {name: "Sales"}){
    group{
      id
      name
      description
      parent {
        id
      }
      members {
        edges {
          node {
            id
          }
        }
      }
      childTeams {
        edges {
          node {
            id
          }
        }
      }
    }
  errors{
    message
    path
    }
  }
}
```

### 🧬 groupCreate (a group within a group, subgroup), get groups first

```graphql
query get_Groups{
  account{
    groups{
      nodes{
        id
        name
        alias
        parent {
          id
        }
      }
    }
  }
}

mutation create_subGroup_for_me_1{
  groupCreate(input: {name: "Sales Subgroup 1", parent:{alias: "Sales"}, teams:{alias: "Sales Team"}}){
    group{
      id
      name
      description
      parent {
        id
      }
    }
  errors{
    message
    path
    }
  }
}
```

### 🧬 infrastructureResourceCreate

Docs:

[Import Infrastructure Objects via API](https://docs.opslevel.com/docs/import-infrastructure-objects-via-api#create-infrastructure-objects-via-graphql-api)

```graphql
# Use with query variables (see below in Notion page)
mutation infrastructureResourceCreate(
  $data: JSON,
  $schema: InfrastructureResourceSchemaInput,
  $providerData: InfrastructureResourceProviderDataInput,
  $providerResourceType: String,
) {
  infrastructureResourceCreate(
    input: {
      data: $data,
      schema: $schema,
      providerData: $providerData,
      providerResourceType: $providerResourceType,
      }
   ) {
    infrastructureResource {
      id
      name
      data
      type
      providerData {
        accountName
        externalUrl
        providerName
      }
      providerResourceType
    }
    warnings {
      message
    }
    errors {
      message
      path
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "infrastructureResourceCreate": {
        "infrastructureResource": {
        "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzM4NzI0Ng",
        "name": "my-gcp-instance",
        "data": {
            "name": "my-gcp-instance",
            "zone": "us-central1-c",
            "image_id": "debian-cloud/debian-11",
            "external_id": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234/zones/us-central1-c/instances/my-gcp-instance",
            "instance_id": "6412763931310737000"
        },
        "type": "Compute",
        "providerData": {
            "accountName": "My First Project",
            "externalUrl": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234",
            "providerName": "GCP"
        },
        "providerResourceType": "Google Compute",
        "owner": null
        },
        "warnings": [],
        "errors": []
    }
  }
}
```
</details>

Query Variables for creating a “Compute” resource

```json
{
  "data": {
    "name": "gke-autoscale-prod-1-example",
    "instance_id": "6412763931310739112",
    "external_id": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234/zones/us-central1-c/instances/gke-autoscale-prod-1-example",
    "image_id": "debian-11-bullseye-v20230615",
    "zone": "us-central1-c",
    "instance_type": "f1-micro",
    "platform_details": "Debian GNU/Linux",
    "launch_time": "2023-06-08T13:26:35.000000",
    "public_ip_address": "--"
  },
  "schema": {"type": "Compute"},
  "providerData": {
    "accountName": "(Example) 5604422034290",
    "externalUrl": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234",
    "providerName": "GCP"
  },
  "providerResourceType": "Compute Engine"
}
```

```json
{
  "data": {
    "name": "gke-author-pages-prod-1",
    "instance_id": "6412763931310739113",
    "external_id": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234/zones/us-central1-c/instances/gke-author-pages-prod-1",
    "image_id": "debian-11-bullseye-v20230615",
    "zone": "us-central1-c",
    "instance_type": "f1-micro",
    "platform_details": "Debian GNU/Linux",
    "launch_time": "2023-06-08T13:26:35.000000",
    "public_ip_address": "--"
  },
  "schema": {"type": "Compute"},
  "providerData": {
    "accountName": "(Example) 5604422034290",
    "externalUrl": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234",
    "providerName": "GCP"
  },
  "providerResourceType": "Compute Engine"
}
```
    

Query Variables for creating a “Database” (SQL) resource

```json
{
  "data": {
    "name": "books-db",
    "external_id": "https://sqladmin.googleapis.com/sql/v1beta4/projects/genial-tangent-1234/instances/books-db",
    "zone": "us-central1",
    "engine": "mySQL",
    "engine_version": "8.0",
    "endpoint": "genial-tangent-1234:us-central1:books-db",
    "multi_zone_availability_enabled": true,
    "publicly_accessible": false,
    "port": 3306,
    "zone": "us-central1",
    "instance_type": "db-n1-standard-1",
    "storage_size": {
      "value": 200,
      "unit": "GB"
    },
    "storage_encrypted": true,
    "maintenance_window": "Monday",
    "creation_date": "2023-06-07T22:01:21.417000Z"
  },
  "schema": {"type": "Database"},
  "providerData": {
    "accountName": "(Example) 5604422034290",
    "externalUrl": "https://console.cloud.google.com/home/dashboard?project=genial-tangent-1234",
    "providerName": "GCP"
  },
  "providerResourceType": "Google SQL"
}
```

Query Variables for creating a “VPC” resource

```json
{
  "data": {
    "name": "gcp-vpc-5",
    "external_id": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234/global/networks/gcp-vpc-5",
    "zone": "global",
    "subnets": [],
    "is_default": true,
    "internet_gateway": "--",
    "dns_hostnames_enabled":false,
    "ipv4_cidr": "--",
    "nat_gateway": "--",
    "dns_support_enabled":false
  },
  "schema": {"type": "Network"},
  "providerData": {
    "accountName": "(Example) 5604422034290",
    "externalUrl": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234",
    "providerName": "GCP"
  },
  "providerResourceType": "Google VPC network"
}
```

### 🧬 infrastructureResourceDelete (get all infrastructure ids first)

Note: Only infrastructure resources created through the API can be deleted with this mutation. If the infrastructure resource was created with the AWS integration, the resource needs to be removed in AWS.

```graphql
query get_all_infra_resources {
  account {
    infrastructureResources {
      nodes {
       id
       name
       href
      }
    }
  }
}

mutation infrastructureResourceDelete{
  infrastructureResourceDelete(resource: {id:"Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjQ1Nw"}){
    deletedId
    errors{
      message
      path
    }
  }
}
```

<details>
  <summary>Example response expand to show</summary>
    
```json
{
  "data": {
    "infrastructureResourceDelete": {
        "deletedId": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxMjQ1Nw",
        "errors": []
    }
  }
}
```
</details>

### 🧬 integrationDelete, get all integrations first, then delete the AWS integration

```graphql
query get_all_integrations{
  account {
    integrations {
     edges {
       node {
         id
         name
        type
       }
     }
    }
  }
}

mutation delete_aws_integration{
  integrationDelete(resource: {id:"Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpBd3NJbnRlZ3JhdGlvbi8yOTM1"}) 
  }
```

<details>
  <summary>Example QUERY response expand to show</summary>
    
```json

{
  "data": {
    "account": {
      "integrations": {
        "edges": [
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
        ]
      }
    }
  }
}
```
</details>
    
<details>
  <summary>Example MUTATION response expand to show</summary>
    
```json
{
  "data": {
    "integrationDelete": {
        "deletedAlias": "arn:aws:iam::694260482182:role/OpsLevelIntegrationRole",
        "deletedId": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpBd3NJbnRlZ3JhdGlvbi8yOTM1"
    }
  }
}
```
</details>
    

### 🧬 relationshipCreate, get all service/infrastructure/system ids first

```graphql

query get_all_services{
  account{
    services{
      totalCount
      pageInfo{
        endCursor
        hasNextPage
      }
      nodes{
        name
        id
        aliases
      }
    }
  }
}

query get_all_infra_resources {
  account {
    infrastructureResources{
      totalCount
      pageInfo{
        endCursor
        hasNextPage
      }
      nodes {
        id
        name
      }
    }
  }
}

query get_all_systems {
  account{
    systems{
      totalCount
      pageInfo{
        endCursor
        hasNextPage
      }
      nodes{
        id
        name
      }
    }
  }
}

# type can be:
# belongs_to (The source resource belongs to the target resource. Assign services and infra to systems.)
# depends_on (The source resource depends on the target resource. Supports: service depends_on services / service depends_on infra / infra depends_on infra / infra depends_on service)

mutation infraRelationshipCreate($source: IdentifierInput!, $target: IdentifierInput!, $type: RelationshipTypeEnum!) {
        relationshipCreate(relationshipDefinition: {
          source: $source,
          target: $target,
          type: $type
        }) {
          relationship {
            id
            type
            source {
              ... on Service {
                id
                name
                 __typename
              }
              ... on System {
                id
                name
                 __typename
              }
              ... on InfrastructureResource {
                id
                name
                __typename
              }
            }
            target {
              ... on Service {
                id
                name
                 __typename
              }
              ... on System {
                id
                name
                 __typename
              }
              ... on Domain {
                id
                name
                 __typename
              }
              ... on InfrastructureResource {
                id
                name
                 __typename
              }
            }
          }
          errors {
            message
            path
          }
        }
      }
```

Query Variables

```json
{
  "source": {"id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIxNjUzOQ"},
  "target": {"id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzEyMDk"},
  "type": "belongs_to"
}
```

```json
{
  "source": { "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzIwMzI" },
  "target": { "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS81MzIwMQ" },
  "type": "depends_on"
}
```

### 🧬 relationshipDelete (by id)

```graphql
mutation relationshipDelete($id: ID!) {
      relationshipDelete (input: {
        id: $id
      }) {
        deletedId
        errors {
          message
          path
        }
      }
    }
```

### 🧬 repositoriesUpdate (hide repositories), get all repository ids first

```graphql
query get_all_repository_ids{
  account{
    repositories{
      pageInfo{
        startCursor
        endCursor
        hasNextPage
      }
      nodes{
        name
        defaultAlias
        id
      }
    }
  }
}

mutation hide_repos{
  repositoriesUpdate(repositories:[{id: "Z2lkOi8vb3BzbGV2ZWwvUmVwb3NpdG9yaWVzOjpHaXRodWIvNTg3Mjg"},{id: "Z2lkOi8vb3BzbGV2ZWwvUmVwb3NpdG9yaWVzOjpHaXRodWIvODcyODc"}], visible: false){
    updatedRepositories{
      name
      id
      visible
    }
    errors{
      message
      path
    }
  }
}
```

### 🧬 repositoriesUpdate (update owners), get all repository aliases and team aliases first

```graphql
query get_all_repository_aliases{
  account{
    repositories{
      pageInfo{
        startCursor
        endCursor
        hasNextPage
      }
      nodes{
        name
        defaultAlias
        owner {
          id
        }
      }
    }
  }
}

query get_all_teams{
  account{
    teams {
      edges {
        node {
          id
          alias
        }
      }
    }
  }
}

mutation update_owner_for_repositories($repositories: [IdentifierInput!]!, $owner: IdentifierInput, $visible: Boolean, $syncLinkedServices: Boolean) {
  repositoriesUpdate(repositories: $repositories, owner: $owner, visible: $visible, syncLinkedServices: $syncLinkedServices) {
    errors {
      message
      path
    }
    updatedRepositories {
      id
      owner {
        alias
      }
      visible
      services {
        nodes {
          name
          owner {
            alias
          }
        }
      }
    }
    notUpdatedRepositories {
      repository {
        id
        name
      }
      error
    }
  }
}
```

Query Variables

```json
{
 "repositories": [
    {
      "alias": "github.com:chucksburgers/python-test"
    },
    {
      "alias": "github.com:chucksburgers/flask-test"
    }
  ],
  "owner": {
    "alias": "frontend"
  },
  "visible": true,
  "syncLinkedServices": true
}
```

### 🧬 repositoriesUpdate (update visibility), get repository aliases first

```graphql
query get_all_repository_aliases{
  account{
    repositories{
      pageInfo{
        startCursor
        endCursor
        hasNextPage
      }
      nodes{
        name
        defaultAlias
        owner {
          id
        }
      }
    }
  }
}

mutation update_visibility_for_repositories($repositories: [IdentifierInput!]!, $visible: Boolean, $syncLinkedServices: Boolean) {
  repositoriesUpdate(repositories: $repositories, visible: $visible, syncLinkedServices: $syncLinkedServices) {
    errors {
      message
      path
    }
    updatedRepositories {
      id
      owner {
        alias
      }
      visible
      services {
        nodes {
          name
          owner {
            alias
          }
        }
      }
    }
    notUpdatedRepositories {
      repository {
        id
        name
      }
      error
    }
  }
}
```

Query Variables

```json
{
 "repositories": [
    {
      "alias": "github.com:chucksburgers/python-test"
    },
    {
      "alias": "github.com:chucksburgers/flask-test"
    }
  ],
  "visible": false,
  "syncLinkedServices": true

}
```

### 🧬 serviceCreate

Example 1

```graphql
mutation create_Service_redis{
  serviceCreate(input:{
    name: "(Example) My First Service", lifecycleAlias: "pre-alpha", tierAlias: "tier_3", framework:"django", language:"python"})
  {
    service {
      name
      description
      owner {
        name
      }
      tier {
        alias
        name
      }
      lifecycle{
        alias
        name
      }
    }
    errors {
      message
      path
    }
  }
}
```


### 🧬 serviceCreate with tagAssign together

Note: This is NOT idempotent

```graphql
# Use with query variables (see below in Notion page)
mutation CreateService_test($alias: String!, $tier: String, $owner: String, $tags: [TagInput!]!) {
  serviceCreate(input: {name: $alias, tierAlias: $tier, ownerAlias: $owner}) {
    service {
      id
      name
      aliases
      htmlUrl
      owner {
        alias
      }
      tier {
        alias
      }
      tags {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          key
          value
        }
      }
    }
    errors {
      message
    }
  }
  tagAssign(input: {type: Service, alias: $alias, tags: $tags}) {
    tags {
      key
      value
    }
    errors {
      message
    }
  }
}
```

Query Variables

```json
{
  "alias": "redis",
  "tier": "tier_4",
  "owner": "partner_team",
  "tags": [
    {"key": "k8s.namespace", "value":"partners"},
    {"key": "public_facing", "value":"true"}
  ],
}
```

### 🧬 serviceRepositoryCreate with repositoryUpdate together

Use case: This mutation will link the repository to their corresponding service, and when you update the owner for the repository, this will be inherited by the linked service.

```graphql
# Use with query variables (see below in Notion page)
mutation serviceRepositoryCreate_and_repositoryUpdate($repository_id: ID!, $service_alias: String!, $ownerId: ID!){
  serviceRepositoryCreate(input: {service: {alias: $service_alias} repository: {id: $repo_id} baseDirectory: "/"} ){
    serviceRepository{
      id
      service {
        id
      }
      repository {
        id
      }
      baseDirectory
    }
    errors{
      message
      path
    }
  }
  repositoryUpdate(input: {id: $repository_id ownerId: $ownerId} syncLinkedServices: true ){
    repository{
      name
      owner {
        id
      }
    }
    errors{
      message
      path
    }
  }
}
```

Query Variables

```json
{
  "repository_id": "Z2lkOi8vb3BzbGV2ZWwvUmVwb3NpdG9yaWVzOjpHaXRodWIvOTI0MzA",
  "service_alias": "2048_service",
  "ownerId": "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8zMjk5"
}
```

### 🧬 tagAssign, assigning tags to a service

If a tag key already exists, tagAssign will replace the value.

```graphql
# Use with query variables (see below in Notion page)
mutation tagAssign_to_a_service($id: ID, $alias: String, $type: TaggableResource, $tags: [TagInput!]!){
tagAssign(input: {id: $id, alias: $alias, type: $type, tags: $tags}){
    tags {
      key
      value
      }
    errors {
      message
      path
    }
  }
}
```

Query Variables

```json
{
  "alias": "redis",
  "tags": [
    {"key": "k8s.namespace", "value":"partners"}
  ]
}
```

### 🧬 tagAssign, assigning tags to a team

```graphql
# Use with query variables (see below in Notion page)
mutation tagAssign_to_a_team($id: ID, $alias: String, $type: TaggableResource, $tags: [TagInput!]!){
  tagAssign(input: {id: $id, alias: $alias, type: $type, tags: $tags}){
    tags {
      key
      value
      }
    errors {
      message
      path
    }
  }
}
```

Query Variables

```json
{
  "alias": "architecture",
  "tags": [
    {"key": "sme", "value":"domains"}
  ],
  "type": "Team"
}
```

### 🧬 tagCreate

```graphql
mutation tagCreate($id: ID, $alias: String, $key: String!, $value: String!){
  tagCreate(input: {id: $id, alias: $alias, key: $key, value: $value}){
    tag{
      id
      key
      value
    }
    errors{
      message
      path
    }
  }
}
```

Query Variables

```json
{
  "alias": "redis",
  "key": "application_name",
  "value": "re_dis2"
}
```

### 🧬 teamMembershipCreate, get all teams first

```graphql
query get_all_teams{
  account{
    teams {
      edges {
        node {
          id
          alias
          aliases
          contacts {
            id
          }
          members {
              nodes{
              name
              email
            }
          }
          manager {
            id
            name
            email
          }
          responsibilities
        }
      }
    }
  }
}

mutation modify_add_user_on_a_team{
  teamMembershipCreate(input: {teamId: "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8xNjg3", members:{email:"ianroy@opslevel.com"}}){
    members{
      email
      name
    }
    errors{
      message
      path
    }
  }
}
```

### 🧬 teamMembershipDelete, get all teams first

```graphql
query get_all_teams{
  account{
    teams {
      edges {
        node {
          id
          alias
          aliases
          contacts {
            id
          }
          members {
              nodes{
              name
              email
            }
          }
          manager {
            id
            name
            email
          }
          responsibilities
        }
      }
    }
  }
}

mutation modify_remove_user_on_a_team{
  teamMembershipDelete(input: {teamId: "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8xNjg3", members:{email:"ianroy@opslevel.com"}}){
    deletedMembers{
      email
      name
    }
    errors{
      message
      path
    }
  }
}
```

### 🧬 teamUpdate, get all teams first

```graphql
query get_all_teams{
  account{
    teams {
      edges {
        node {
          id
          alias
          aliases
          contacts {
            id
          }
          members {
              nodes{
              name
              email
            }
          }
          manager {
            id
            name
            email
          }
          responsibilities
        }
      }
    }
  }
}

mutation modify_manager_of_a_team{
  teamUpdate(input: {id: "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8xNjg3", managerEmail: "ianroy@opslevel.com"}){
    team{
      manager{
        name
      }
    }
    errors{
      path
      message
    }
  }
}
```

