variable "github_org" {
  description = "GitHub organization to read repositories from."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the OpsLevel team that owns the GitHub token secret."
  type        = string
}

variable "manage_secrets" {
  description = "Create the OpsLevel secret holding the GitHub token. Set false if it already exists."
  type        = bool
  default     = true
}

variable "github_token" {
  description = "GitHub fine-grained token: your org as resource owner, all repositories, Repository permission Metadata: Read."
  type        = string
  sensitive   = true
  default     = null
}
