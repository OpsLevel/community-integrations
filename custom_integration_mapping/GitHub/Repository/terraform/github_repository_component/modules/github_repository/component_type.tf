# The GitHub Repository component type: one component per repository, so maturity checks can run on
# repositories (OpsLevel checks don't run on the repository object itself). Every property is written by the
# "GitHub Repositories" custom integration from GitHub repo metadata, so all are locked in the UI.
resource "opslevel_component_type" "github_repository" {
  name        = var.component_type_name
  alias       = var.component_type_alias
  description = var.component_type_description
  icon = {
    color = "#4096ff"
    name  = "PhCode"
  }

  properties = {
    age_in_months = {
      name                    = "Age(in months)"
      description             = "Whole calendar months since repo creation, recomputed each run"
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "integer"
        "minimum" = 0
      })
    }
    archived = {
      name                    = "archived"
      description             = "Boolean that shows whether a repository is archived or not"
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "boolean"
      })
    }
    creation_date = {
      name                    = "Creation Date"
      description             = "Date the repo was Created in Github"
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "string"
        "format" = "date-time"
      })
    }
    empty = {
      name                    = "empty"
      description             = "Marks repositories detected as empty by Github sync. Defaults to false when value is missing."
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "boolean"
      })
    }
    github_id = {
      name                    = "Github ID"
      description             = "The Github ID of the repository"
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "integer"
        "minimum" = 0
      })
    }
    repository_description = {
      name                    = "Repository Description"
      description             = "The description of the repository as listed in Github."
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "string"
      })
    }
    repository_name = {
      name                    = "Repository Name"
      description             = "The full name of the repository in github"
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "string"
      })
    }
    updated_date = {
      name                    = "Updated Date"
      description             = "- date the repo last had changes\n- this would be useful for finding out which repos might be stale or no longer used"
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "string"
        "format" = "date-time"
      })
    }
    visibility = {
      name                    = "Visibility"
      description             = "The ability for people in and out of the organization to be able to view the repository"
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "string"
        "pattern" = "^[A-Za-z]+$"
      })
    }
    github_topics = {
      name                    = "GitHub Topics"
      description             = "Topics set on the repository in GitHub."
      display_status          = "visible"
      allowed_in_config_files = false
      locked_status           = "ui_locked"
      schema = jsonencode({
        "type" = "array"
        "items" = {
          "type" = "string"
        }
        "uniqueItems" = true
      })
    }
  }

  # Manual link back to the Service/Backend/Frontend/etc. the repository belongs to (no automatic link exists:
  # managed relationship rules can't match on attached repositories).
  relationships = {
    component = {
      name               = "Component"
      description        = "The component (Service, Backend, Frontend, ...) this repository belongs to. Set by hand."
      allowed_categories = ["default"]
    }
  }
}
