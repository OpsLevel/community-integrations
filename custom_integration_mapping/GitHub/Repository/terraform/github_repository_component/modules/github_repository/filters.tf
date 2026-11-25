# Custom-property predicates name the property by alias in key_data; the component_type_id predicate keeps
# them to GitHub Repository components.
resource "opslevel_filter" "active" {
  name       = "GitHub Repositories (active)"
  connective = "and"
  predicate {
    key   = "component_type_id"
    type  = "equals"
    value = opslevel_component_type.github_repository.id
  }
  predicate {
    key      = "properties"
    key_data = "archived"
    type     = "satisfies_jq_expression"
    value    = ". != true"
  }
}

resource "opslevel_filter" "high_risk" {
  name       = "GitHub Repositories - High risk (P1/P2)"
  connective = "and"
  predicate {
    key   = "filter_id"
    type  = "matches"
    value = opslevel_filter.active.id
  }
  predicate {
    key      = "properties"
    key_data = "risk_priority"
    type     = "satisfies_jq_expression"
    value    = ". == \"P1\" or . == \"P2\""
  }
}
