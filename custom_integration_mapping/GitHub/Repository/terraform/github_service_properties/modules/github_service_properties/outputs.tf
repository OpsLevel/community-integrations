output "property_definition_ids" {
  value = { for k, p in opslevel_property_definition.github : k => p.id }
}

output "expected_property_aliases" {
  description = "Aliases the transform writes to. Compare with Settings > Service properties after apply."
  value       = local.property_aliases
}

output "scorecard_id" {
  value = opslevel_scorecard.github_risk.id
}

output "filter_ids" {
  value = {
    active    = opslevel_filter.active.id
    high_risk = opslevel_filter.high_risk.id
  }
}
