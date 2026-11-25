terraform {
  required_version = ">= 1.5"
  required_providers {
    opslevel = {
      source  = "OpsLevel/opslevel"
      version = ">= 1.14.0" # opslevel_check_tag_defined, opslevel_service_tag
    }
  }
}
