variable "component_type_id" {
  description = "Id of the GitHub Repository component type: the github_repository module's component_type_id output."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the team that owns the scorecard and its checks."
  type        = string
}

# --- risk tags ---
variable "repo_classifications" {
  description = "Per repository (GitHub repo name): data_classification, external_interface_type and optionally risk_priority (derived when null). Set as tags on its GitHub Repository component."
  type = map(object({
    data_classification     = string
    external_interface_type = string
    risk_priority           = optional(string)
  }))
  default = {}
  validation {
    condition = alltrue([for c in values(var.repo_classifications) :
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
  default = "(Use Case) Security - GitHub Repository Risk"
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
