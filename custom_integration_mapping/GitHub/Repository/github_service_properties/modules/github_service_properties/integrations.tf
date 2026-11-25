# Pull: GitHub org repos -> repo metadata on the matching Service.
resource "opslevel_integration_custom" "github_service_properties" {
  name = var.integration_name
  etl_definition = {
    extract_definition = templatefile("${path.module}/definitions/github_repos_extract.yaml.tftpl", {
      github_org                = var.github_org
      github_token_secret_alias = var.github_token_secret_alias
    })
    transform_definition = templatefile("${path.module}/definitions/github_repos_transform.yaml.tftpl", {
      a = local.property_aliases
    })
  }

  depends_on = [opslevel_property_definition.github, opslevel_secret.github_token]
}
