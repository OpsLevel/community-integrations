output "property_definition_ids" {
  description = "Property definition ids by key (repo_id, archived, description, ...); input to the risk scorecard module."
  value       = { for k, p in opslevel_property_definition.github : k => p.id }
}

output "expected_property_aliases" {
  description = "Aliases the transform writes to. Compare with Settings > Service properties after apply."
  value       = local.property_aliases
}
