## 🧬 Mutations

### 🧬 aliasCreate for a service, get services first

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

### 🧬 aliasDelete for a service, get services first

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

mutation aliasDelete_for_a_service{
  aliasDelete(input:{ownerType:service, alias:"catalog_service"}){
    deletedAlias
    errors{
      message
      path
    }
  }
}
```

### 🧬 awsIntegrationUpdate, get AWS integrations first, then reactivate integration if invalidated

Note: `integrationReactivate` will reactivate the integration and OpsLevel will
retry syncing resources on the next scheduled sync. This is only required if 
the integration was invalidated (`invalidatedAt` is not null).

```graphql
query integrations_aws {
  account {
    integrations(type: "aws") {
      nodes {
        ... on AwsIntegration {
          name
          id
          externalId
          invalidatedAt
          invalidatedReason
          regionOverride
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}

mutation awsIntegrationUpdate($awsIntegrationId: ID, $regionOverrideList: [String!]) {
  awsIntegrationUpdate(
    integration: {id: $awsIntegrationId}
    input: {regionOverride: $regionOverrideList}
  ) {
    integration {
      ... on AwsIntegration {
        name
        id
        externalId
        invalidatedAt
        invalidatedReason
        regionOverride
      }
    }
    errors {
      message
      path
    }
  }
}

mutation integrationReactivate($awsIntegrationId: ID) {
  integrationReactivate(integration: {id: $awsIntegrationId}) {
    integration{
      ... on AwsIntegration{
        name
        id
        externalId
        regionOverride
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
  "awsIntegrationId": "Z2lkOi8vb3BzbGV2ZWwvSW50ZWdyYXRpb25zOjpBd3NJbnRlZ3JhdGlvbi81OT69",
  "regionOverrideList": [
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-south-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    "ap-southeast-4",
    "ap-southeast-5",
    "ca-central-1",
    "ca-west-1",
    "eu-central-1",
    "eu-central-2",
    "eu-north-1",
    "eu-south-1",
    "eu-south-2",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "il-central-1",
    "me-central-1",
    "me-south-1",
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2"
  ]
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


### 🧬 infrastructureResourceCreate

Docs:

[Import Infrastructure Objects via API](https://docs.opslevel.com/docs/import-infrastructure-objects-via-api#create-infrastructure-objects-via-graphql-api)

```graphql
# Use with query variables below
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

### 🧬 infrastructureResourceUpdate (get all infrastructure ids first)

Notes: 
* Only infrastructure resources created through the API can be updated with this mutation. If the infrastructure resource was created with the AWS integration, the resource needs to be removed in AWS.
* Include existing and new values in data. It is a full overwrite, not an incremental update. Currently set fields not included in data will disappear.

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
```

```graphql
mutation infrastructureResourceUpdate(
  $infrastructureResourceAlias:String,
  $infrastructureResourceID:ID,
  $ownerId:ID,
  $data:JSON,
  $schema: InfrastructureResourceSchemaInput,
  $providerData: InfrastructureResourceProviderDataInput,
  $providerResourceType: String,
){
  infrastructureResourceUpdate(
    infrastructureResource:{alias:$infrastructureResourceAlias,id:$infrastructureResourceID}
    input:{
      data:$data
      ownerId:$ownerId
      schema:$schema
      providerData:$providerData
      providerResourceType:$providerResourceType
    }
  ){
    infrastructureResource{
      id
      name
      owner{
        ... on Team{
          name
        }
      }
      data
      rawData
    }
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
    "infrastructureResourceUpdate": {
      "infrastructureResource": {
        "id": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzI5MzQxMjA",
        "name": "gke-catalog-service-prod-1",
        "owner": {
          "name": "Order Management Team"
        },
        "data": {
          "name": "gke-catalog-service-prod-1",
          "zone": "us-central1-c",
          "image_id": "debian-11-bullseye-v20230615",
          "external_id": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234/zones/us-central1-c/instances/gke-catalog-service-prod-1",
          "instance_id": "6412763931310739113",
          "launch_time": "2024-07-17T13:26:35.000000",
          "instance_type": "f1-micro",
          "platform_details": "Debian GNU/Linux",
          "public_ip_address": "--"
        },
        "rawData": {
          "name": "gke-catalog-service-prod-1",
          "zone": "us-central1-c",
          "image_id": "debian-11-bullseye-v20230615",
          "external_id": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234/zones/us-central1-c/instances/gke-catalog-service-prod-1",
          "instance_id": "6412763931310739113",
          "launch_time": "2024-07-17T13:26:35.000000",
          "instance_type": "f1-micro",
          "platform_details": "Debian GNU/Linux",
          "public_ip_address": "--"
        }
      },
      "errors": []
    }
  }
}
```
</details>

Query Variables for updating an existing "Compute” resource

```json
{
  "infrastructureResourceAlias": "",
  "infrastructureResourceID": "Z2lkOi8vb3BzbGV2ZWwvRW50aXR5T2JqZWN0LzI5MzQxMjA",
  "ownerId": "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8xNjUx",
  "data": {
    "name": "gke-catalog-service-prod-1",
    "instance_id": "6412763931310739113",
    "external_id": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234/zones/us-central1-c/instances/gke-catalog-service-prod-1",
    "image_id": "debian-11-bullseye-v20230615",
    "zone": "us-central1-c",
    "instance_type": "f1-micro",
    "platform_details": "Debian GNU/Linux",
    "launch_time": "2024-07-17T13:26:35.000000",
    "public_ip_address": "--"
  },
  "schema": {
    "type": "Compute"
  },
  "providerData": {
    "accountName": "(Example) 5604422034290",
    "externalUrl": "https://www.googleapis.com/compute/v1/projects/genial-tangent-1234",
    "providerName": "GCP"
  },
  "providerResourceType": "Compute Engine"
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

### 🧬 propertyAssign (assign a value to a service/component custom property), get all propertyDefinitions and services first

```graphql
query get_all_properties_for_each_componentTypes {
  account {
    componentTypes {
      nodes {
        id
        name
        properties {
          nodes {
            id
            name
            alias
            description
            schema
          }
          pageInfo {
            endCursor
            hasNextPage
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

query get_all_services($endCursor: String) {
  account {
    services(after: $endCursor) {
      nodes {
        id
        name
        aliases
        properties {
          nodes {
            definition {
              name
            }
            value
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

# boolean, see query variables below for boolean example
mutation propertyAssign_boolean($owning_object_id: ID, $owning_object_alias: String, $property_definition_id: ID, $property_definition_alias: String, $property_value: JsonString!, $runValidation: Boolean) {
  propertyAssign(
    input: {owner: {id: $owning_object_id, alias: $owning_object_alias}, definition: {id: $property_definition_id, alias: $property_definition_alias}, value: $property_value, runValidation: $runValidation}
  ) {
    property {
      definition {
        id
        name
      }
      value
      validationErrors {
        message
        path
      }
      owner {
        ... on Service {
          id
          name
        }
      }
    }
    errors {
      message
      path
    }
  }
}

# string, see query variables below for string example
mutation propertyAssign_string($owning_object_id: ID, $owning_object_alias: String, $property_definition_id: ID, $property_definition_alias: String, $property_value: JsonString!, $runValidation: Boolean) {
  propertyAssign(
    input: {owner: {id: $owning_object_id, alias: $owning_object_alias}, definition: {id: $property_definition_id, alias: $property_definition_alias}, value: $property_value, runValidation: $runValidation}
  ) {
    property {
      owner {
        ... on Service {
          name
        }
      }
      definition {
        ... on PropertyDefinition {
          name
        }
      }
      value
      validationErrors {
        message
        path
      }
    }
    errors {
      message
      path
    }
  }
}
```

Query variables:

```json
# boolean
{
  "owning_object_alias": "shopping_cart",
  "property_definition_alias": "publicly_routable",
  "property_value": "true",
  "runValidation": true
}

# string
{
  "owning_object_alias": "shopping_cart",
  "property_definition_alias": "service_cost_last_30_days",
  "property_value": "\"$15,000\"",
  "runValidation": true
}
```


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
# Use with query variables below
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
# Use with query variables below
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
# Use with query variables below
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
# Use with query variables below
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

### 🧬 tagAssign, assigning tags to a user

```graphql
# Use with query variables below
mutation tagAssign_to_a_user($id: ID, $alias: String, $type: TaggableResource, $tags: [TagInput!]!){
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
  "id": "Z2lkOi8vb3BzbGV2ZWwvVXNlci80MjIw",
  "tags": [
    {"key": "sme", "value":"kubectl-opslevel"},
    {"key": "country", "value": "CA"},
    {"key": "role", "value": "Lead Customer Support Engineer"}
  ],
  "type": "User"
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

