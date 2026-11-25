# Levels by rubric index (1 = Bronze, 2 = Silver, 3 = Gold, 4 = Diamond if the account has it). Checks written
# for a level above var.rubric_level_count go on the highest available level instead.
data "opslevel_rubric_level" "level" {
  for_each = toset([for i in range(1, var.rubric_level_count + 1) : tostring(i)])
  filter {
    field = "index"
    value = each.value
  }
}

resource "opslevel_scorecard" "github_risk" {
  name                           = var.scorecard_name
  owner_id                       = data.opslevel_team.owner.id
  filter_id                      = opslevel_filter.active.id
  affects_overall_service_levels = var.scorecard_affects_overall_levels
  description                    = <<-EOT
    Risk-based standards for services, from their GitHub repository. Each service's **risk_priority** tag (P1-P4) comes from its **data_classification** tag (public, internal, confidential, restricted) and **external_interface_type** tag (none, internal_api, public_api, public_web). P1 = confidential or restricted data behind a public interface.

    - **Bronze**: the service is classified (data_classification and external_interface_type tags set).
    - **Silver**: it has a description and isn't P1.
    - **Gold**: P1/P2 repos aren't public.
    - **Diamond** (Gold in accounts with three levels): P1/P2 services' repos are actively maintained, and the service's risk is P3 or lower.

    Only services with GitHub repo metadata are in scope; services whose repository is archived are out of scope.
  EOT
}

locals {
  scorecard_category = opslevel_scorecard.github_risk.categories[0]

  # kind = "tag": Tag Defined check on the risk tags (tags.tf). kind = "property": Custom Property check on the
  # Service type's GitHub properties, jq run against the property value. high_risk = true: only P1/P2 repos (the check's
  # filter excludes the rest, so they aren't held back).
  checks = {
    data_classification_is_set = {
      kind = "tag", name = "Data classification tag is set", level = "1", high_risk = false
      key  = "data_classification", predicate = "matches_regex", value = "^(public|internal|confidential|restricted)$"
      notes = "Tag the service `data_classification`: public, internal, confidential or restricted."
    }
    external_interface_type_is_set = {
      kind = "tag", name = "External interface type tag is set", level = "1", high_risk = false
      key  = "external_interface_type", predicate = "matches_regex", value = "^(none|internal_api|public_api|public_web)$"
      notes = "Tag the service `external_interface_type`: none, internal_api, public_api or public_web."
    }
    repository_has_a_description = {
      kind = "property", name = "Repository has a description", level = "2", high_risk = false
      key  = "description", predicate = "satisfies_jq_expression", value = "type == \"string\" and test(\"\\\\S\")"
      notes = "Add a description to the service's repository in GitHub so owners and reviewers know what it holds."
    }
    not_a_p1_risk = {
      kind = "tag", name = "Not a P1 risk", level = "2", high_risk = false
      key  = "risk_priority", predicate = "does_not_equal", value = "P1"
      notes = "P1 means confidential or restricted data behind a public interface. Reduce exposure (internal-only interface, private repo) or confirm the classification with security."
    }
    high_risk_repository_is_not_public = {
      kind = "property", name = "High risk: repository is not public", level = "3", high_risk = true
      key  = "visibility", predicate = "satisfies_jq_expression", value = ". != \"public\""
      notes = "P1/P2 repos hold sensitive data or expose public interfaces; make the repository private or internal."
    }
    high_risk_pushed_to_in_the_last_90_days = {
      kind = "property", name = "High risk: pushed to in the last 90 days", level = "4", high_risk = true
      key  = "last_pushed_at", predicate = "satisfies_jq_expression", value = "(sub(\"\\\\.[0-9]+\"; \"\") | fromdateiso8601) > (now - 7776000)"
      notes = "Unmaintained P1/P2 repos miss security fixes. Ship a change, or archive the repo if it's no longer used."
    }
    risk_priority_p3_or_lower = {
      kind = "tag", name = "Risk priority P3 or lower", level = "4", high_risk = false
      key  = "risk_priority", predicate = "matches_regex", value = "^P[34]$"
      notes = "Lower the repo's risk: narrow its external interface or move sensitive data out of it."
    }
  }
}

locals {
  check_level  = { for k, c in local.checks : k => data.opslevel_rubric_level.level[tostring(min(tonumber(c.level), var.rubric_level_count))].id }
  check_filter = { for k, c in local.checks : k => c.high_risk ? opslevel_filter.high_risk.id : null }
}

resource "opslevel_check_service_property" "this" {
  for_each = { for k, c in local.checks : k => c if c.kind == "property" }

  name                = each.value.name
  category            = local.scorecard_category
  level               = local.check_level[each.key]
  owner               = data.opslevel_team.owner.id
  enabled             = var.checks_enabled
  filter              = local.check_filter[each.key]
  property            = "custom_property"
  component_type      = data.opslevel_component_type.service.id
  property_definition = var.property_definition_ids[each.value.key]
  predicate = {
    type  = each.value.predicate
    value = each.value.value
  }
  notes = each.value.notes
}

resource "opslevel_check_tag_defined" "this" {
  for_each = { for k, c in local.checks : k => c if c.kind == "tag" }

  name     = each.value.name
  category = local.scorecard_category
  level    = local.check_level[each.key]
  owner    = data.opslevel_team.owner.id
  enabled  = var.checks_enabled
  filter   = local.check_filter[each.key]
  tag_key  = each.value.key
  tag_predicate = {
    type  = each.value.predicate
    value = each.value.value
  }
  notes = each.value.notes
}
