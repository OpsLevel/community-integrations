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

resource "opslevel_filter" "high_risk" {
  name       = "Services with a GitHub repo - High risk (P1/P2)"
  connective = "and"
  predicate {
    key   = "filter_id"
    type  = "matches"
    value = opslevel_filter.active.id
  }
  predicate {
    key      = "properties"
    key_data = opslevel_property_definition.github["risk_priority"].id
    type     = "satisfies_jq_expression"
    value    = ". == \"P1\" or . == \"P2\""
  }
}
