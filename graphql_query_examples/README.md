# GraphQL API Query Examples

## Overview

Interact with OpsLevel using our GraphQL API to query and mutate data on your own OpsLevel account using examples available here.

Learn more about our GraphQL API in our [docs](https://docs.opslevel.com/docs/graphql).

## How to navigate, view, and use examples

The examples are best viewed in `Preview` mode in GitHub's UI, alongside using the auto-generated Table of Contents button to search and filter by header. See GitHub's [blog post](https://github.blog/changelog/2021-04-13-table-of-contents-support-in-markdown-files/) on accessing the auto-generated Table of Contents.

Copy the query and query variables and jump into the [GraphiQL Explorer](https://app.opslevel.com/graphiql) to try out the examples below.

> [!WARNING]  
> Please note that mutations will modify data in your account. Use caution when using these examples.


## Examples

Query examples: [graphql_query_examples.md](./graphql_query_examples.md)

Mutation examples: see [graphql_mutation_examples.md](./graphql_mutation_examples.md)


## Templates for adding examples

Example Templates

Query:

````md
  ### 🔎 queryFieldName (query for everything/specific) > nestedQueryFieldName (if applicable)

  Use Case:

  ```graphql
  query exampleQueryFieldName{
    account{
        something
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
        }
      }
    }
  }
  ```
  </details>

````

Mutation:

````md
  ### 🔎 mutationFieldName, get input data (ids/aliases/etc) first

  Use Case:

  ```graphql
  query exampleQueryFieldName{
    account{
        something
    }
  }

  mutation exampleMutationFieldName{
    exampleCreate(input: {key1: "value1", key2: "value2"}){
        something
    }
    errors{
      message
      path
    }
  }
  ```

  Query Variables
  ```json
  {
    key1: "value1",
    key2: "value2"
  }
  ```

  <details>
    <summary>Example response expand to show</summary>
    
  ```json
  {
    "data": {
      "account": {
        "services": {
        }
      }
    }
  }
  ```
  </details>

````