variable "github_org" {
  description = "GitHub organization whose repositories become GitHub Repository components."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the team that owns the GitHub token secret."
  type        = string
}

# --- component type ---
variable "component_type_name" {
  type    = string
  default = "GitHub Repository"
}

variable "component_type_alias" {
  description = "Can't change after creation; the transform writes components of this type."
  type        = string
  default     = "github_repository"
}

variable "component_type_description" {
  type    = string
  default = "One component per GitHub repository, created and kept up to date by the GitHub Repositories custom integration (repo metadata, visibility, dates)."
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
