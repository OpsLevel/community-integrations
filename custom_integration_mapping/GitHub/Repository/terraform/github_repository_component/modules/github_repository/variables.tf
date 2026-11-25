variable "github_org" {
  description = "GitHub organization whose repositories become GitHub Repository components."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the team that owns the scorecard, its checks and the secrets."
  type        = string
}

# --- component type ---
variable "component_type_name" {
  type    = string
  default = "GitHub Repository"
}

variable "component_type_alias" {
  description = "Can't change after creation; the transform, checks and filters reference the type by its id."
  type        = string
  default     = "github_repository"
}

variable "component_type_description" {
  type    = string
  default = "One component per GitHub repository, created and kept up to date by the GitHub Repositories custom integration (repo metadata, visibility, dates, data classification and external interface type for risk-based checks)."
}

# --- integrations ---
variable "github_integration_name" {
  type    = string
  default = "Integration Data Mapping (Pull) - GitHub Repositories"
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
