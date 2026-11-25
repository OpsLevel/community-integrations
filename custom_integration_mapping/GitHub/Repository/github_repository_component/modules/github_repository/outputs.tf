output "component_type_id" {
  description = "Id of the GitHub Repository component type (input to the risk scorecard module)."
  value       = opslevel_component_type.github_repository.id
}

output "component_type_alias" {
  value = opslevel_component_type.github_repository.alias
}

output "github_integration_webhook_url" {
  description = "Not used by the pull extractor; listed for completeness."
  value       = opslevel_integration_custom.github_repositories.webhook_url
  sensitive   = true
}
