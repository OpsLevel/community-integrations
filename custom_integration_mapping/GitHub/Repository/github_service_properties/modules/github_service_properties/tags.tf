# Risk classification as OpsLevel tags on Services, set from var.service_classifications (keyed by Service alias;
# instead of GitHub custom properties, which would need configuring in GitHub). Three tags per service:
#   data_classification      public | internal | confidential | restricted
#   external_interface_type  none | internal_api | public_api | public_web
#   risk_priority            P1-P4: set explicitly, or derived below
#
# Derived risk_priority, a suggested default (impact x exposure, not from a published standard):
#   confidential/restricted + public_api/public_web = P1; confidential/restricted, or internal + public = P2;
#   internal, or public data + public interface = P3; otherwise P4.
locals {
  classifications = {
    for svc, c in var.service_classifications : svc => merge(c, {
      risk_priority = coalesce(c.risk_priority, (
        contains(["confidential", "restricted"], c.data_classification) && contains(["public_api", "public_web"], c.external_interface_type) ? "P1" :
        contains(["confidential", "restricted"], c.data_classification) || (c.data_classification == "internal" && contains(["public_api", "public_web"], c.external_interface_type)) ? "P2" :
        c.data_classification == "internal" || contains(["public_api", "public_web"], c.external_interface_type) ? "P3" : "P4"
      ))
    })
  }

  repo_tags = merge([
    for svc, c in local.classifications : {
      for key in ["data_classification", "external_interface_type", "risk_priority"] :
      "${svc}/${key}" => { service = svc, key = key, value = c[key] }
    }
  ]...)
}

resource "opslevel_service_tag" "risk" {
  for_each = local.repo_tags

  service_alias = each.value.service
  key           = each.value.key
  value         = each.value.value
}
