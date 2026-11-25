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

# The custom integration (same as github_repository_component/example) ...
module "github_repository" {
  source = "../../../github_repository_component/modules/github_repository"

  github_org       = var.github_org
  owner_team_alias = var.owner_team_alias

  manage_secrets = var.manage_secrets
  github_token   = var.github_token
}

# ... plus risk tags, filters and the scorecard on its component type.
module "github_repository_risk" {
  source = "../../modules/github_repository_risk"

  component_type_id    = module.github_repository.component_type_id
  owner_team_alias     = var.owner_team_alias
  rubric_level_count   = var.rubric_level_count
  repo_classifications = var.repo_classifications
}
