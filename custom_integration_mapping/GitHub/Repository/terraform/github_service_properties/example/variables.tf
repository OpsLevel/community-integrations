variable "github_org" {
  description = "GitHub organization to read repositories from."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the OpsLevel team that owns the scorecard, checks and secret."
  type        = string
}

variable "rubric_level_count" {
  description = "Rubric levels above Beginner in the account (3 = Bronze/Silver/Gold; 4 adds Diamond)."
  type        = number
  default     = 3
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
