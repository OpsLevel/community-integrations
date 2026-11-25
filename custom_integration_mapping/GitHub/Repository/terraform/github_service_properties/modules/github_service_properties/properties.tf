# GitHub repo metadata as custom properties on the default component type (Service). opslevel_property_definition
# has no alias argument: OpsLevel derives the alias from the name (lowercase, spaces -> "_"), and the transform
# writes properties by alias. local.property_aliases holds the expected aliases; if OpsLevel derives a different
# one (Settings > Service > properties), correct it there and re-apply.
locals {
  properties = {
    repo_id = {
      name   = "GitHub Repo ID"
      desc   = "The GitHub ID of the repository."
      schema = { type = "integer", minimum = 0 }
    }
    full_name = {
      name   = "GitHub Repo Full Name"
      desc   = "owner/name of the repository in GitHub."
      schema = { type = "string" }
    }
    description = {
      name   = "GitHub Repo Description"
      desc   = "The repository description in GitHub."
      schema = { type = "string" }
    }
    visibility = {
      name   = "GitHub Repo Visibility"
      desc   = "public, private or internal."
      schema = { type = "string", pattern = "^[A-Za-z]+$" }
    }
    archived = {
      name   = "GitHub Repo Archived"
      desc   = "Whether the repository is archived in GitHub."
      schema = { type = "boolean" }
    }
    empty = {
      name   = "GitHub Repo Empty"
      desc   = "True when GitHub reports the repository as empty (size 0)."
      schema = { type = "boolean" }
    }
    created_at = {
      name   = "GitHub Repo Created At"
      desc   = "When the repository was created in GitHub."
      schema = { type = "string", format = "date-time" }
    }
    last_pushed_at = {
      name   = "GitHub Repo Last Pushed At"
      desc   = "Last push to the repository: when it last had changes. Useful for finding stale repositories."
      schema = { type = "string", format = "date-time" }
    }
    age_in_months = {
      name   = "GitHub Repo Age In Months"
      desc   = "Whole calendar months since the repository was created, recomputed each sync."
      schema = { type = "integer", minimum = 0 }
    }
    languages = {
      name   = "GitHub Repo Languages"
      desc   = "The repository's primary language as reported by GitHub."
      schema = { type = "array", items = { type = "string" }, minItems = 1, maxItems = 8, uniqueItems = true }
    }
    topics = {
      name   = "GitHub Repo Topics"
      desc   = "Topics set on the repository in GitHub."
      schema = { type = "array", items = { type = "string" }, uniqueItems = true }
    }
  }

  # Expected alias for each property (derived from its name), used by the transform.
  property_aliases = { for k, p in local.properties : k => replace(lower(p.name), " ", "_") }
}

resource "opslevel_property_definition" "github" {
  for_each = local.properties

  name                    = each.value.name
  description             = each.value.desc
  schema                  = jsonencode(each.value.schema)
  allowed_in_config_files = false       # set by the integration, not opslevel.yml
  locked_status           = "ui_locked" # only the integration (API) writes them
  property_display_status = "visible"
}
