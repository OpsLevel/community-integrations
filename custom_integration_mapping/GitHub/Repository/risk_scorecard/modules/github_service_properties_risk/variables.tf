variable "property_definition_ids" {
  description = "Property definition ids by key: the github_service_properties module's property_definition_ids output. Needs repo_id, archived, description, visibility and last_pushed_at."
  type        = map(string)
}

variable "owner_team_alias" {
  description = "Alias of the team that owns the scorecard and its checks."
  type        = string
}

# --- Service type ---
variable "service_type_alias" {
  description = "Alias of the component type the properties are on: the account's default type (usually Service). opslevel_property_definition always creates on the default type."
  type        = string
  default     = "service"
}

# --- risk tags ---
variable "service_classifications" {
  description = "Per Service alias: data_classification, external_interface_type and optionally risk_priority (derived when null). Set as tags on the Service."
  type = map(object({
    data_classification     = string
    external_interface_type = string
    risk_priority           = optional(string)
  }))
  default = {}
  validation {
    condition = alltrue([for c in values(var.service_classifications) :
      contains(["public", "internal", "confidential", "restricted"], c.data_classification) &&
      contains(["none", "internal_api", "public_api", "public_web"], c.external_interface_type) &&
      (c.risk_priority == null || contains(["P1", "P2", "P3", "P4"], coalesce(c.risk_priority, "P4")))
    ])
    error_message = "data_classification: public|internal|confidential|restricted; external_interface_type: none|internal_api|public_api|public_web; risk_priority: P1-P4."
  }
}

# --- scorecard ---
variable "scorecard_name" {
  type    = string
  default = "(Use Case) Security - Service GitHub Repository Risk"
}

variable "scorecard_affects_overall_levels" {
  type    = bool
  default = false
}

variable "rubric_level_count" {
  description = "Rubric levels above Beginner (index 1..N) the account has. With 3, the two Diamond checks go on Gold."
  type        = number
  default     = 3
  validation {
    condition     = var.rubric_level_count >= 1 && var.rubric_level_count <= 4
    error_message = "rubric_level_count must be between 1 and 4."
  }
}

variable "checks_enabled" {
  type    = bool
  default = true
}
