data "opslevel_component_type" "service" {
  identifier = var.service_type_alias
}

# Services that have GitHub repo metadata and whose repo isn't archived. Custom-property predicates reference
# the property definition by id.
resource "opslevel_filter" "active" {
  name       = "Services with a GitHub repo (active)"
  connective = "and"
  predicate {
    key   = "component_type_id"
    type  = "equals"
    value = data.opslevel_component_type.service.id
  }
  predicate {
    key      = "properties"
    key_data = opslevel_property_definition.github["repo_id"].id
    type     = "exists"
  }
  predicate {
    key      = "properties"
    key_data = opslevel_property_definition.github["archived"].id
    type     = "satisfies_jq_expression"
    value    = ". != true"
  }
}

# risk_priority tag is P1 or P2 (a filter has one connective, so the OR lives in its own filter).
resource "opslevel_filter" "risk_p1_p2" {
  name       = "Services - risk_priority P1 or P2"
  connective = "or"
  predicate {
    key      = "tags"
    key_data = "risk_priority"
    type     = "equals"
    value    = "P1"
  }
  predicate {
    key      = "tags"
    key_data = "risk_priority"
    type     = "equals"
    value    = "P2"
  }
}

resource "opslevel_filter" "high_risk" {
  name       = "Services with a GitHub repo - High risk (P1/P2)"
  connective = "and"
  predicate {
    key   = "filter_id"
    type  = "matches"
    value = opslevel_filter.active.id
  }
  predicate {
    key   = "filter_id"
    type  = "matches"
    value = opslevel_filter.risk_p1_p2.id
  }
}
