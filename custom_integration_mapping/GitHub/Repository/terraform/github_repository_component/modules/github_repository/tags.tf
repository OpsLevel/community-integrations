# Risk classification as OpsLevel tags on the GitHub Repository components, set from var.repo_classifications
# (instead of GitHub custom properties, which would need configuring in GitHub). Three tags per repo:
#   data_classification      public | internal | confidential | restricted
#   external_interface_type  none | internal_api | public_api | public_web
#   risk_priority            P1-P4: set explicitly, or derived below
#
# Derived risk_priority, a suggested default (impact x exposure, not from a published standard):
#   confidential/restricted + public_api/public_web = P1; confidential/restricted, or internal + public = P2;
#   internal, or public data + public interface = P3; otherwise P4.
#
# The components must exist first: they're created by the integration's first sync, so on a new account run
# `apply` once, Sync the integration, then `apply` again to add the tags.
locals {
  classifications = {
    for repo, c in var.repo_classifications : repo => merge(c, {
      risk_priority = coalesce(c.risk_priority, (
        contains(["confidential", "restricted"], c.data_classification) && contains(["public_api", "public_web"], c.external_interface_type) ? "P1" :
        contains(["confidential", "restricted"], c.data_classification) || (c.data_classification == "internal" && contains(["public_api", "public_web"], c.external_interface_type)) ? "P2" :
        c.data_classification == "internal" || contains(["public_api", "public_web"], c.external_interface_type) ? "P3" : "P4"
      ))
    })
  }

  repo_tags = merge([
    for repo, c in local.classifications : {
      for key in ["data_classification", "external_interface_type", "risk_priority"] :
      "${repo}/${key}" => { repo = repo, key = key, value = c[key] }
    }
  ]...)
}

resource "opslevel_service_tag" "risk" {
  for_each = local.repo_tags

  # Components are named "GitHub Repo - <repo>", so OpsLevel gives each the alias github_repo_-_<repo>.
  service_alias = "github_repo_-_${lower(each.value.repo)}"
  key           = each.value.key
  value         = each.value.value
}
