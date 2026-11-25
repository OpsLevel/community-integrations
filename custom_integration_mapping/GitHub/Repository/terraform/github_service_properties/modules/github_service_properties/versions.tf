terraform {
  required_version = ">= 1.5"
  required_providers {
    opslevel = {
      source  = "OpsLevel/opslevel"
      version = ">= 1.14.0" # opslevel_integration_custom with etl_definition
    }
  }
}
