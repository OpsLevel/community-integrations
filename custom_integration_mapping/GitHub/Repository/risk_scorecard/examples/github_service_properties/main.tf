terraform {
  required_version = ">= 1.5"
  required_providers {
    opslevel = {
      source  = "OpsLevel/opslevel"
      version = "~> 1.14"
    }
  }
}

# Token from OPSLEVEL_API_TOKEN (write access). Set OPSLEVEL_API_URL if your account isn't on app.opslevel.com.
provider "opslevel" {}

# The custom integration (same as github_service_properties/example) ...
module "github_service_properties" {
  source = "../../../github_service_properties/modules/github_service_properties"

  github_org       = var.github_org
  owner_team_alias = var.owner_team_alias

  manage_secrets = var.manage_secrets
  github_token   = var.github_token
}

# ... plus risk tags, filters and the scorecard on the Services it writes to.
module "github_service_properties_risk" {
  source = "../../modules/github_service_properties_risk"

  property_definition_ids = module.github_service_properties.property_definition_ids
  owner_team_alias        = var.owner_team_alias
  rubric_level_count      = var.rubric_level_count
  service_classifications = var.service_classifications
}
