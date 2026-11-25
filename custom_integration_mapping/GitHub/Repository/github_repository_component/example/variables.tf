variable "github_org" {
  description = "GitHub organization to read repositories from."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the OpsLevel team that owns the GitHub token secret."
  type        = string
}

variable "manage_secrets" {
  description = "Create the OpsLevel secret holding the GitHub token (needs github_token). Default false: create the github_api_token secret in OpsLevel yourself."
  type        = bool
  default     = false
}

variable "github_token" {
  description = "GitHub fine-grained token: your org as resource owner, all repositories, Repository permission Metadata: Read."
  type        = string
  sensitive   = true
  default     = null
}
