variable "github_org" {
  description = "GitHub organization whose repository metadata is written onto matching Services."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the team that owns the GitHub token secret."
  type        = string
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
