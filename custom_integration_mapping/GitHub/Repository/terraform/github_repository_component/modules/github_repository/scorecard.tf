# Levels by rubric index (1 = Bronze, 2 = Silver, 3 = Gold, 4 = Diamond if the account has it). Checks written
# for a level above var.rubric_level_count go on the highest available level instead.
data "opslevel_rubric_level" "level" {
  for_each = toset([for i in range(1, var.rubric_level_count + 1) : tostring(i)])
  filter {
    field = "index"
    value = each.value
  }
}

resource "opslevel_scorecard" "github_repository_risk" {
  name                           = var.scorecard_name
  owner_id                       = data.opslevel_team.owner.id
  filter_id                      = opslevel_filter.active.id
  affects_overall_service_levels = var.scorecard_affects_overall_levels
  description                    = <<-EOT
    Risk-based standards for GitHub repositories. Each repo's **Risk Priority** (P1-P4) comes from two GitHub custom properties: **data classification** (public, internal, confidential, restricted) and **external interface type** (none, internal_api, public_api, public_web), one step higher when a public repo holds non-public data. P1 = confidential or restricted data behind a public interface.

    - **Bronze**: the repo is classified (both custom properties set in GitHub).
    - **Silver**: it has a description and isn't P1.
    - **Gold**: P1/P2 repos aren't public.
    - **Diamond** (Gold in accounts with three levels): P1/P2 repos are actively maintained, and the repo's risk is P3 or lower.

    Archived repositories are out of scope.
  EOT
}

locals {
  scorecard_category = opslevel_scorecard.github_repository_risk.categories[0]

  # Custom Property checks on the GitHub Repository type. Each predicate is jq run against the property value.
  # high_risk = true: only P1/P2 repos (the check's filter excludes the rest, so they aren't held back).
  checks = {
    data_classification_is_set = {
      name      = "Data classification is set"
      level     = "1"
      property  = "data_classification"
      jq        = "IN(\"public\", \"internal\", \"confidential\", \"restricted\")"
      high_risk = false
      notes     = "Set the `data_classification` custom property on the repo in GitHub (Settings > Custom properties): public, internal, confidential or restricted."
    }
    external_interface_type_is_set = {
      name      = "External interface type is set"
      level     = "1"
      property  = "external_interface_type"
      jq        = "IN(\"none\", \"internal_api\", \"public_api\", \"public_web\")"
      high_risk = false
      notes     = "Set the `external_interface_type` custom property on the repo in GitHub: none, internal_api, public_api or public_web."
    }
    repository_has_a_description = {
      name      = "Repository has a description"
      level     = "2"
      property  = "repository_description"
      jq        = "type == \"string\" and test(\"\\\\S\")"
      high_risk = false
      notes     = "Add a description to the repository in GitHub so owners and reviewers know what it holds."
    }
    not_a_p1_risk = {
      name      = "Not a P1 risk"
      level     = "2"
      property  = "risk_priority"
      jq        = ". != \"P1\""
      high_risk = false
      notes     = "P1 means confidential or restricted data behind a public interface. Reduce exposure (internal-only interface, private repo) or confirm the classification with security."
    }
    high_risk_repository_is_not_public = {
      name      = "High risk: repository is not public"
      level     = "3"
      property  = "visibility"
      jq        = ". != \"public\""
      high_risk = true
      notes     = "P1/P2 repos hold sensitive data or expose public interfaces; make the repository private or internal."
    }
    high_risk_pushed_to_in_the_last_90_days = {
      name      = "High risk: pushed to in the last 90 days"
      level     = "4"
      property  = "updated_date"
      jq        = "(sub(\"\\\\.[0-9]+\"; \"\") | fromdateiso8601) > (now - 7776000)"
      high_risk = true
      notes     = "Unmaintained P1/P2 repos miss security fixes. Ship a change, or archive the repo if it's no longer used."
    }
    risk_priority_p3_or_lower = {
      name      = "Risk priority P3 or lower"
      level     = "4"
      property  = "risk_priority"
      jq        = ". == \"P3\" or . == \"P4\""
      high_risk = false
      notes     = "Lower the repo's risk: narrow its external interface or move sensitive data out of it."
    }
  }
}

resource "opslevel_check_service_property" "this" {
  for_each = local.checks

  name                = each.value.name
  category            = local.scorecard_category
  level               = data.opslevel_rubric_level.level[tostring(min(tonumber(each.value.level), var.rubric_level_count))].id
  owner               = data.opslevel_team.owner.id
  enabled             = var.checks_enabled
  filter              = each.value.high_risk ? opslevel_filter.high_risk.id : null
  property            = "custom_property"
  component_type      = opslevel_component_type.github_repository.id
  property_definition = each.value.property
  predicate = {
    type  = "satisfies_jq_expression"
    value = each.value.jq
  }
  notes = each.value.notes
}
