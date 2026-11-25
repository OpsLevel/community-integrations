output "component_type_id" {
  value = opslevel_component_type.github_repository.id
}

output "github_integration_webhook_url" {
  description = "Not used by the pull extractor; listed for completeness."
  value       = opslevel_integration_custom.github_repositories.webhook_url
  sensitive   = true
}

output "scorecard_id" {
  value = opslevel_scorecard.github_repository_risk.id
}

output "filter_ids" {
  value = {
    active    = opslevel_filter.active.id
    high_risk = opslevel_filter.high_risk.id
  }
}
