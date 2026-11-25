output "scorecard_id" {
  value = opslevel_scorecard.github_risk.id
}

output "filter_ids" {
  value = {
    active     = opslevel_filter.active.id
    risk_p1_p2 = opslevel_filter.risk_p1_p2.id
    high_risk  = opslevel_filter.high_risk.id
  }
}
