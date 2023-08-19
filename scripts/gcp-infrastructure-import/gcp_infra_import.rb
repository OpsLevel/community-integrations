
# typed: true
# frozen_string_literal: true

require "JSON"
TOKEN = "XXXXXXXXXXXXXXXXXXXXXX"
instance_details = JSON.parse(File.read("instances.json"))

instance = instance_details["items"][0]
endpoint = "https://api.opslevel.com/graphql"

data = {
  name: instance["name"],
  instance_id: instance["id"],
  instance_type: instance["machineType"].split("/").last,
  zone: instance["zone"].split("/").last,
  vpc: instance["networkInterfaces"][0]["network"].split("/").last,
  launch_time: instance["creationTimestamp"],
  volume_list: [{
    type: instance["disks"][0]["type"],
    storage_size: {
      value: instance["disks"][0]["diskSizeGb"].to_i,
      unit: "GB",
    },
  }],
}

variables = {
  data: data,
  schema: {
    type: "Compute",
  },
  providerData: {
    accountName: "ci-gcp",
    externalUrl: "https://console.cloud.google.com",
    providerName: "GCP",
  },
}

mutation = "{\"query\":\"mutation infrastructureResourceCreate($ownerId: ID, $data: JSON, $schema: InfrastructureResourceSchemaInput, $providerData: InfrastructureResourceProviderDataInput, $providerResourceType: String) {  infrastructureResourceCreate(input: {ownerId: $ownerId, data: $data, schema: $schema, providerData: $providerData, providerResourceType: $providerResourceType}) {    infrastructureResource {      id      name      data      type      providerData {        accountName        externalUrl        providerName      }      providerResourceType      owner {        ... on Team {          name        }        ... on Group {          name        }      }    }    warnings {      message    }    errors {      message      path    }  }}\",\"variables\": #{variables.to_json},\"operationName\":\"infrastructureResourceCreate\"}"

puts "curl '#{endpoint}' -X POST -H \"Authorization: Bearer #{TOKEN}\" -H 'accept: application/json' -H 'accept-language: en-US,en;q=0.9' -H 'cache-control: no-cache' -H 'content-type: application/json'  --data-raw '#{mutation}' "

system("curl '#{endpoint}' -X POST -H \"Authorization: Bearer #{TOKEN}\" -H 'accept: application/json' -H 'accept-language: en-US,en;q=0.9' -H 'cache-control: no-cache' -H 'content-type: application/json'  --data-raw '#{mutation}' ")
