variable "github_org" {
  description = "GitHub organization whose repository metadata is written onto matching Services."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the team that owns the scorecard, its checks and the secrets."
  type        = string
}

# --- Service type ---
variable "service_type_alias" {
  description = "Alias of the component type the properties are on: the account's default type (usually Service). opslevel_property_definition always creates on the default type."
  type        = string
  default     = "service"
}

# --- integrations ---
variable "integration_name" {
  type    = string
  default = "Integration Data Mapping (Pull) - GitHub Repo Metadata on Services"
}

# --- secrets ---
variable "manage_secrets" {
  description = "Create the OpsLevel secret the GitHub extractor reads. Set false when they already exist in the account."
  type        = bool
  default     = true
}

variable "github_token_secret_alias" {
  type    = string
  default = "github_api_token"
}

variable "github_token" {
  description = "GitHub fine-grained PAT: resource owner = the org, all repositories, Repository permission Metadata: Read."
  type        = string
  sensitive   = true
  default     = null
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
