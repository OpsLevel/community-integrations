variable "github_org" {
  description = "GitHub organization to read repositories from."
  type        = string
}

variable "owner_team_alias" {
  description = "Alias of the OpsLevel team that owns the GitHub token secret (and, with the risk scorecard, the scorecard and checks)."
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

variable "rubric_level_count" {
  description = "Rubric levels above Beginner in the account (3 = Bronze/Silver/Gold; 4 adds Diamond)."
  type        = number
  default     = 3
}

variable "repo_classifications" {
  description = "Per GitHub repo name: data_classification, external_interface_type, optional risk_priority (set as tags)."
  type = map(object({
    data_classification     = string
    external_interface_type = string
    risk_priority           = optional(string)
  }))
  default = {}
}
