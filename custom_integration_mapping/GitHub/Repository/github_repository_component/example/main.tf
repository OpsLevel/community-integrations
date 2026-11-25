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

module "github_repository" {
  source = "../modules/github_repository"

  github_org       = var.github_org
  owner_team_alias = var.owner_team_alias

  manage_secrets = var.manage_secrets
  github_token   = var.github_token
}
