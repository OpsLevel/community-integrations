# Pull: GitHub org repos -> one GitHub Repository component each ("GitHub Repo - <name>"), with repo metadata.
resource "opslevel_integration_custom" "github_repositories" {
  name = var.github_integration_name
  etl_definition = {
    extract_definition = templatefile("${path.module}/definitions/github_repos_extract.yaml.tftpl", {
      github_org                = var.github_org
      github_token_secret_alias = var.github_token_secret_alias
    })
    transform_definition = file("${path.module}/definitions/github_repos_transform.yaml")
  }

  # The transform writes these properties and creates components of this type.
  depends_on = [opslevel_component_type.github_repository, opslevel_secret.github_token]
}
