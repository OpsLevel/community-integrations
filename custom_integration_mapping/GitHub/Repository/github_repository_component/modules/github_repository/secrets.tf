data "opslevel_team" "owner" {
  alias = var.owner_team_alias
}

resource "opslevel_secret" "github_token" {
  count = var.manage_secrets ? 1 : 0
  alias = var.github_token_secret_alias
  owner = data.opslevel_team.owner.id
  value = var.github_token

  lifecycle {
    precondition {
      condition     = var.github_token != null
      error_message = "Set github_token, or manage_secrets = false if the secret already exists."
    }
  }
}
