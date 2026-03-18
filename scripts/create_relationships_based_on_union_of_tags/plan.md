The goal is to use a script to query for all of the infrastructure resources from OpsLevel, read in specific tags from infrastructure components, and based on the union of certain tags, create the relationship on the default components.

Query the relationshipDefinitions, find any relationshipDefinitions with "service_tag_key" in it, grab the string, split on comma, and parse the key:value, this will determine the following rules:

* for `relationshipDefinitionId` use the id
* for `service_tag_key`, use the value as the tag key to read in
* for `service_tag_value`, use the componentType.alias
* for `environment_tag_key`, use the value as the tag key to read in
* for `environment_tag_value`, use the value as the value

Find infrastructure components with the `environment_tag_key` and `environment_tag_value` e.g. `environment:staging`, read in the `service_tag_key` and `service_tag_value` e.g. `service:shopping_cart`. If those 2 tags are found, create a relationship using the relationshipCreate mutation with the needed variables.

Queries needed:

```graphql
query get_components_default($endCursor: String) {
  account {
    services(after: $endCursor, componentCategory: "default") {
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

example response:

```json
{
  "data": {
    "account": {
      "services": {
        "pageInfo": {
          "endCursor": "Nw",
          "hasNextPage": true
        },
        "nodes": [
          {
            "name": "Shopping Cart Service",
            "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQzMg",
            "aliases": [
              "Shopping Cart",
              "Shopping Cart Service",
              "basket_service",
              "cart",
              "devops_shopping_cart_service",
              "gandalfsbooks/shopping_cart",
              "grocery_cart",
              "k8s:production/shopping_cart",
              "ol_demo_shopping_cart",
              "shopping-cart",
              "shopping-cart-gcp-sg-008-prod",
              "shopping-cart-service",
              "shopping_cart",
              "shopping_cart_service",
              "shoppingcart",
              "shoppingcart-freestyle",
              "shoppingcartservice"
            ],
            "timestamps": {
              "createdAt": "2021-12-02T16:39:11.783358Z",
              "updatedAt": "2026-03-10T10:18:53.655111Z"
            },
            "owner": {
              "name": "Order Management Team",
              "alias": "order_management_team",
              "id": "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8xOTA1"
            },
            "language": "Ruby",
            "framework": "Rails",
            "lifecycle": {
              "name": "Generally Available"
            },
            "tier": {
              "name": "Tier 1"
            },
            "parent": {
              "name": "Cart System",
              "__typename": "System",
              "parent": {
                "name": "e-Commerce",
                "__typename": "Domain"
              }
            },
            "product": "Retail Website",
            "properties": {
              "nodes": [
                {
                  "definition": {
                    "name": "(Draft) Check opt-out"
                  },
                  "value": "[\"no_check1\",\"no_check2\",\"no_check3\"]"
                },
                {
                  "definition": {
                    "name": "AWS Cost"
                  },
                  "value": "61447.89"
                },
                {
                  "definition": {
                    "name": "Annual Attestation of Completeness and Accuracy"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "Auto Deployed"
                  },
                  "value": "false"
                },
                {
                  "definition": {
                    "name": "Current Container Image"
                  },
                  "value": "{\"build_date\":\"2024-01-03T18:25:43-05:00\",\"container_id\":\"8b97850f-3ace-42da-974c-62e19a5c9ddb\",\"container_name\":\"gcr.io/shopping_cart_service_image\"}"
                },
                {
                  "definition": {
                    "name": "Data Class"
                  },
                  "value": "[\"internal\",\"public\"]"
                },
                {
                  "definition": {
                    "name": "Environments"
                  },
                  "value": "[\"prod\",\"staging\"]"
                },
                {
                  "definition": {
                    "name": "GitHub Topics"
                  },
                  "value": "[\"external\",\"generally-available\",\"public\",\"test\"]"
                },
                {
                  "definition": {
                    "name": "Languages"
                  },
                  "value": "[\"Go\",\"Java\"]"
                },
                {
                  "definition": {
                    "name": "Last Deployed Version"
                  },
                  "value": "\"prod-a2c4e6g8-1742842669\""
                },
                {
                  "definition": {
                    "name": "Product"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "Publicly Routable"
                  },
                  "value": "true"
                },
                {
                  "definition": {
                    "name": "Service Cost (Last 30 days)"
                  },
                  "value": "\"$10,002.00\""
                },
                {
                  "definition": {
                    "name": "VPCEnabled"
                  },
                  "value": "true"
                },
                {
                  "definition": {
                    "name": "readme_file_present"
                  },
                  "value": "true"
                }
              ]
            },
            "tags": {
              "nodes": [
                {
                  "key": "a11ytarget",
                  "value": "L3",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzMzMDA3MzIw"
                },
                {
                  "key": "auto_deployed",
                  "value": "false",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzc5NDMwMzAy"
                },
                {
                  "key": "data-class",
                  "value": "internal",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzc5NDg5Mjc3"
                },
                {
                  "key": "db",
                  "value": "mysql",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzU2OTk5Ng"
                },
                {
                  "key": "environment",
                  "value": "shopping-cart-demo",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzc5MzczNTI5"
                },
                {
                  "key": "environment",
                  "value": "shopping-cart-production",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzc5MzczNTMx"
                },
                {
                  "key": "environment",
                  "value": "shopping-cart-staging",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzc5MzczNTMz"
                },
                {
                  "key": "github_slug",
                  "value": "shopping_cart",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzE2OTY0Mjc1Mg"
                },
                {
                  "key": "kafka-topic",
                  "value": "cart-additions",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzU2OTk5Nw"
                },
                {
                  "key": "pd_id",
                  "value": "PHHMSFU",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzY0MzI4Mjk"
                },
                {
                  "key": "product",
                  "value": "retail_website",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzE2Nzk3ODE"
                },
                {
                  "key": "product",
                  "value": "mobile_app",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzE2Nzk3ODI"
                },
                {
                  "key": "production_version",
                  "value": "1.1.0",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzE3NzM1MDQ"
                },
                {
                  "key": "public-facing",
                  "value": "true",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzk4Mzc5MA"
                },
                {
                  "key": "rails-version",
                  "value": "5.2.6",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzU2OTk5OA"
                },
                {
                  "key": "related_test_slug",
                  "value": "shopping_cart_service",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzI2ODIxMDYwMA"
                },
                {
                  "key": "reorg-aug-2025",
                  "value": "true",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzE5OTM5NjczMw"
                },
                {
                  "key": "role",
                  "value": "http",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzIxOTY2MTkyMg"
                },
                {
                  "key": "staging_version",
                  "value": "2.0.0-rc1",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzE3NzM1MDU"
                },
                {
                  "key": "version",
                  "value": "2.8.0",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzE2OTkzNDYzNg"
                }
              ]
            },
            "relatedResources": {
              "edges": [
                {
                  "relationshipType": "belongs_to",
                  "relationshipDefinition": null,
                  "node": {
                    "__typename": "System"
                  }
                },
                {
                  "relationshipType": "depends_on",
                  "relationshipDefinition": null,
                  "node": {
                    "__typename": "InfrastructureResource"
                  }
                },
                {
                  "relationshipType": "depends_on",
                  "relationshipDefinition": null,
                  "node": {
                    "__typename": "InfrastructureResource"
                  }
                },
                {
                  "relationshipType": "depends_on",
                  "relationshipDefinition": null,
                  "node": {
                    "__typename": "InfrastructureResource"
                  }
                },
                {
                  "relationshipType": "depends_on",
                  "relationshipDefinition": null,
                  "node": {
                    "__typename": "InfrastructureResource"
                  }
                },
                {
                  "relationshipType": "depends_on",
                  "relationshipDefinition": null,
                  "node": {
                    "__typename": "InfrastructureResource"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yMw",
                    "name": "Deploys To"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8zNDU1NTU",
                    "name": "GCP Production",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yMw",
                    "name": "Deploys To"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8zNDU1NTY",
                    "name": "GCP Staging",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNg",
                    "name": "Support Team"
                  },
                  "node": {
                    "__typename": "Team"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NTE3MDA",
                    "name": "web-001",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80Njc4NjM",
                    "name": "analytics-analytics-2301-eu-west-2",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80Njc5ODg",
                    "name": "Table_0001",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNDQ",
                    "name": "Database"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDQ",
                    "name": "db-mysql-000",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDQ",
                    "name": "db-mysql-000",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNzg1",
                    "name": "Production Resources"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDQ",
                    "name": "db-mysql-000",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNDQ",
                    "name": "Database"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDU",
                    "name": "db-mysql-001",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDU",
                    "name": "db-mysql-001",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNzg2",
                    "name": "Staging Resources"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDU",
                    "name": "db-mysql-001",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8xNzI0",
                    "name": "Write to Database"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDg",
                    "name": "db-mysql-004",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgzMTY",
                    "name": "payment-handler-00030",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgzMTA",
                    "name": "auth-handler-00024",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgzNTE",
                    "name": "order-worker-00065",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80Njg0MTY",
                    "name": "notify-service-00130",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80Njg0MzI",
                    "name": "ingest-service-00144",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
                    "name": "Infrastructure"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80Njg0ODI",
                    "name": "billing-service-00196",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNDkw",
                    "name": "Kubernetes Resources"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS84NTc0ODA",
                    "name": "Shopping Cart Production",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yMw",
                    "name": "Deploys To"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMjUzNzg3",
                    "name": "shopping-cart-gcp-sg-008-prod-argocd",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNDkw",
                    "name": "Kubernetes Resources"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xNzI0OTYz",
                    "name": "Shopping Cart Service",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "is_related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yNjY",
                    "name": "Service"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS84NTc0ODA",
                    "name": "Shopping Cart Production",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "is_related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8xNTc",
                    "name": "Associated Service"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xNTQzMTI2",
                    "name": "GAN-24",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "is_related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8xNTc",
                    "name": "Associated Service"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xNTQzMTM5",
                    "name": "GAN-16",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "is_related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8xNTc",
                    "name": "Associated Service"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xNTQzMTY4",
                    "name": "BE-36",
                    "__typename": "Service"
                  }
                },
                {
                  "relationshipType": "is_related_to",
                  "relationshipDefinition": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yNjY",
                    "name": "Service"
                  },
                  "node": {
                    "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xNzI0OTYz",
                    "name": "Shopping Cart Service",
                    "__typename": "Service"
                  }
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

```graphql
query get_components_infrastructure($endCursor: String) {
  account {
    services(after: $endCursor, componentCategory: "infrastructure") {
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

example response:

```json
{
  "data": {
    "account": {
      "services": {
        "pageInfo": {
          "endCursor": "Mg",
          "hasNextPage": true
        },
        "nodes": [
          {
            "name": "analytics-analytics-2301-eu-west-2",
            "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80Njc4NjM",
            "aliases": [
              "analytics-analytics-2301-eu-west-2",
              "arn:aws:s3:::analytics-analytics-2301-eu-west-2"
            ],
            "timestamps": {
              "createdAt": "2025-09-25T18:35:06.690843Z",
              "updatedAt": "2025-12-16T16:15:55.058388Z"
            },
            "owner": {
              "name": "Order Management Team",
              "alias": "order_management_team",
              "id": "Z2lkOi8vb3BzbGV2ZWwvVGVhbS8xOTA1"
            },
            "language": null,
            "framework": null,
            "lifecycle": null,
            "tier": null,
            "parent": null,
            "product": null,
            "properties": {
              "nodes": [
                {
                  "definition": {
                    "name": "ARN"
                  },
                  "value": "\"arn:aws:s3:::analytics-analytics-2301-eu-west-2\""
                },
                {
                  "definition": {
                    "name": "AWS Account ID"
                  },
                  "value": "\"\""
                },
                {
                  "definition": {
                    "name": "AWS Cost"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "AWS Region"
                  },
                  "value": "\"eu-west-2\""
                },
                {
                  "definition": {
                    "name": "Owner"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "Public"
                  },
                  "value": "false"
                },
                {
                  "definition": {
                    "name": "URL"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "Versioned"
                  },
                  "value": "true"
                },
                {
                  "definition": {
                    "name": "name"
                  },
                  "value": "\"analytics-analytics-2301-eu-west-2\""
                }
              ]
            },
            "tags": {
              "nodes": [
                {
                  "key": "app_name",
                  "value": "shopping_cart_service",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzI0NDEzOTA2Mg"
                },
                {
                  "key": "environment",
                  "value": "production",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzI5MDEzMDU4Mg"
                },
                {
                  "key": "owner",
                  "value": "order_management_team",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzI1NDAxOTkyNA"
                },
                {
                  "key": "service",
                  "value": "analytics",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzI5MDEzMDU3Ng"
                }
              ]
            }
          },
          {
            "name": "analytics-analytics-7681-ap-northeast-1",
            "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80Njc5MjA",
            "aliases": [
              "analytics-analytics-7681-ap-northeast-1",
              "arn:aws:s3:::analytics-analytics-7681-ap-northeast-1"
            ],
            "timestamps": {
              "createdAt": "2025-09-25T18:35:12.801163Z",
              "updatedAt": "2025-09-25T18:35:12.801163Z"
            },
            "owner": null,
            "language": null,
            "framework": null,
            "lifecycle": null,
            "tier": null,
            "parent": null,
            "product": null,
            "properties": {
              "nodes": [
                {
                  "definition": {
                    "name": "ARN"
                  },
                  "value": "\"arn:aws:s3:::analytics-analytics-7681-ap-northeast-1\""
                },
                {
                  "definition": {
                    "name": "AWS Account ID"
                  },
                  "value": "\"\""
                },
                {
                  "definition": {
                    "name": "AWS Cost"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "AWS Region"
                  },
                  "value": "\"ap-northeast-1\""
                },
                {
                  "definition": {
                    "name": "Owner"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "Public"
                  },
                  "value": "false"
                },
                {
                  "definition": {
                    "name": "URL"
                  },
                  "value": null
                },
                {
                  "definition": {
                    "name": "Versioned"
                  },
                  "value": "false"
                },
                {
                  "definition": {
                    "name": "name"
                  },
                  "value": "\"analytics-analytics-7681-ap-northeast-1\""
                }
              ]
            },
            "tags": {
              "nodes": [
                {
                  "key": "environment",
                  "value": "staging",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzI5MDEzMDYyMQ"
                },
                {
                  "key": "service",
                  "value": "catalog_service",
                  "id": "Z2lkOi8vb3BzbGV2ZWwvVGFnLzI2NTAxMjA2MA"
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

```graphql
query relationshipDefinitions($endCursor: String){
  account{
    relationshipDefinitions(after: $endCursor, componentType: {alias: "service"}){
      nodes{
        id
        name
        description
        componentType{
          name
          alias
        }
      }
      pageInfo{
        hasNextPage
        endCursor
      }
    }
  }
}
```

example response:

```json
{
  "data": {
    "account": {
      "relationshipDefinitions": {
        "nodes": [
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNDQ",
            "name": "Database",
            "description": "Services read from this database",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yMw",
            "name": "Deploys To",
            "description": "Track what Cloud Provider the component deploys to.\n\nDEMO the ability to assign OpsLevel metadata as values.",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8yOTUw",
            "name": "Infrastructure",
            "description": "Automatically link infrastructure to Services via tags.",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNDkw",
            "name": "Kubernetes Resources",
            "description": "",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNzg1",
            "name": "Production Resources",
            "description": "service_tag_key:service,environment_tag_key:environment,environment_tag_value:production",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNzg2",
            "name": "Staging Resources",
            "description": "service_tag_key:service,environment_tag_key:environment,environment_tag_value:staging",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNg",
            "name": "Support Team",
            "description": "The Support Team is responsible for addressing incidents for this component.\n\nDEMO the ability to assign OpsLevel metadata as values.",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          },
          {
            "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8xNzI0",
            "name": "Write to Database",
            "description": "",
            "componentType": {
              "name": "Service",
              "alias": "service"
            }
          }
        ],
        "pageInfo": {
          "hasNextPage": false,
          "endCursor": "OA"
        }
      }
    }
  }
}
```

mutation to create relationships:

```graphql
mutation relationshipCreate($source: IdentifierInput!, $target: IdentifierInput!, $type: RelationshipTypeEnum!, $relationshipDefinition: IdentifierInput) {
  relationshipCreate(
    relationshipDefinition: {source: $source, target: $target, type: $type, relationshipDefinition: $relationshipDefinition}
  ) {
    relationship {
      id
      type
      source {
        ... on Service {
          id
          name
          __typename
        }
        ... on Team {
          id
          name
          __typename
        }
        __typename
      }
      target {
        ... on Service {
          id
          name
          __typename
        }
        ... on Team {
          id
          name
          __typename
        }
        __typename
      }
      __typename
    }
    errors {
      message
      path
      __typename
    }
    __typename
  }
}
```

query variables:

```json
{
    "source": {
        "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS8xMzQzMg"
    },
    "target": {
        "id": "Z2lkOi8vb3BzbGV2ZWwvU2VydmljZS80NjgxMDU"
    },
    "type": "related_to",
    "relationshipDefinition": {
        "id": "Z2lkOi8vb3BzbGV2ZWwvUmVsYXRpb25zaGlwRGVmaW5pdGlvbi8zNzg2"
    }
}
```

