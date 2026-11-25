# Pull: GitHub org repos -> one GitHub Repository component each ("GitHub Repo - <name>"), with metadata and
# a computed Risk Priority (P1-P4) from the data_classification / external_interface_type GitHub custom properties.
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
