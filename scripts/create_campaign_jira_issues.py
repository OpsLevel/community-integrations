#!/usr/bin/env python3

from __future__ import annotations

import enum
import os
import time
from dataclasses import dataclass
from typing import Any, NoReturn

import requests
import typer
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

load_dotenv()

console = Console()
err_console = Console(stderr=True)

JIRA_URL = "https://{YOUR TEAM}.atlassian.net"
JIRA_PROJECTS_URL = f"{JIRA_URL}/browse/"
JIRA_APITOKEN = os.environ["JIRA_APITOKEN"]
JIRA_USER = os.environ["JIRA_USER"]  # Your email address tied to Jira
OPSLEVEL_APITOKEN = os.environ["OPSLEVEL_APITOKEN"]
OPSLEVEL_ENDPOINT = "https://api.opslevel.com/graphql"
OPSLEVEL_JIRA_SERVICE_LABEL_PREFIX = "opslevel-campaign-service-"


class Action(enum.Enum):
    CREATE = 1
    NO_JIRA = 2
    NO_ISSUE_TYPE = 3
    NOOP = 4


@dataclass
class Account:
    id: str


@dataclass
class Change:
    action: Action
    service: Service
    team: Team
    issue: Issue | None = None


@dataclass
class Campaign:
    id: str
    name: str
    url: str
    brief: str

    @property
    def label(self):
        return f"opslevel-campaign-{self.id}"


@dataclass
class Issue:
    key: str


@dataclass
class Service:
    name: str
    owner: str

    @property
    def name_label(self):
        # Jira labels cannot contain spaces.
        return self.name.replace(" ", "-")

    @property
    def label(self):
        return f"{OPSLEVEL_JIRA_SERVICE_LABEL_PREFIX}{self.name_label}"


@dataclass
class Team:
    name: str
    jira_project: str
    jira_project_id: str = ""
    issue_type_name: str = ""
    issue_type: str = ""


def main(
    campaign_url: str = typer.Argument(..., help="The URL of the OpsLevel campaign")
):
    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        progress.add_task(description="Fetching campaign...", total=None)
        campaign = fetch_campaign(campaign_url)

        progress.add_task(description="Fetching services...", total=None)
        services = fetch_incomplete_services(campaign)

        progress.add_task(description="Fetching teams...", total=None)
        teams = fetch_teams()

        check_campaign_teams(services, teams)

        progress.add_task(description="Fetching campaign issues...", total=None)
        issues = fetch_campaign_jira_issues(campaign)

        set_jira_metadata(teams)

    changes = build_changes(services, issues, teams)
    display_table(changes)

    typer.confirm("Proceed with creating the necessary Jira issues?", abort=True)
    create_issues(changes, campaign)


def fetch_campaign(campaign_url: str) -> Campaign:
    """Fetch the campaign.

    The ID is the campaign URL is not part of the public schema,
    so this function is forced to scan through all the open campaigns
    to find a match.
    """
    open_campaigns_query = """query {
      account {
        campaigns(filter: {key: status, type: does_not_equal, arg:"ended"}) {
          nodes {
            id
            name
            htmlUrl
            projectBrief
          }
        }
      }
    }"""
    data = run_opslevel_query(open_campaigns_query)
    campaigns = data["data"]["account"]["campaigns"]["nodes"]
    for campaign in campaigns:
        if campaign_url == campaign["htmlUrl"]:
            return Campaign(
                campaign["id"],
                campaign["name"],
                campaign["htmlUrl"],
                campaign["projectBrief"],
            )

    fatal(f"No campaign found for {campaign_url}")


def fetch_incomplete_services(campaign: Campaign) -> list[Service]:
    """Fetch all the services that have not completed the campaign."""

    query = """query GetCampaignReport($id: ID!) {
      account {
        campaign(id: $id) {
          id
          name
          services(after: "%s") {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
              id
              name
              owner {
                name
              }
              campaignReport(campaignIds: [$id]) {
                checkResultsByCampaign {
                  nodes {
                    status
                  }
                }
              }
            }
          }
        }
      }
    }"""

    # GraphQL pagination is annoying. This while loops slurps up all the data.
    raw_services = []
    cursor = ""
    variables = {"id": campaign.id}
    has_next_page = True
    while has_next_page:
        data = run_opslevel_query(
            query=query % cursor,
            variables=variables,
            operation_name="GetCampaignReport",
        )
        services_data = data["data"]["account"]["campaign"]["services"]
        page_info = services_data["pageInfo"]
        raw_services.extend(services_data["nodes"])
        cursor = page_info["endCursor"]
        has_next_page = page_info["hasNextPage"]

    services = [
        Service(
            s["name"],
            s["owner"]["name"] if s["owner"] is not None else "NO-OWNER",
        )
        for s in raw_services
        if s["campaignReport"]["checkResultsByCampaign"]["nodes"][0]["status"]
        == "failing"
    ]
    return sorted(services, key=lambda x: (x.owner, x.name))


def fetch_teams() -> dict[str, Team]:
    """Fetch all the teams from OpsLevel.

    The return is a dict keyed by team name for quick lookups.
    """
    query = """query {
      account {
        teams {
          pageInfo {
            hasNextPage
          }
          nodes {
            name
            contacts {
              displayName
              address
            }
          }
        }
      }
    }"""
    data = run_opslevel_query(query)

    # Sanity check to make sure pagination slurping isn't needed.
    if data["data"]["account"]["teams"]["pageInfo"]["hasNextPage"]:
        fatal(
            "There are now multiple pages of teams. "
            "This script must be updated to fetch all the teams."
        )

    team_nodes = data["data"]["account"]["teams"]["nodes"]
    teams = []
    for team_node in team_nodes:
        jira_project = ""
        for contact in team_node["contacts"]:
            if contact["displayName"].lower() == "jira":
                parts = contact["address"].split(JIRA_PROJECTS_URL)
                if len(parts) == 2 and parts[1].isalpha():
                    jira_project = parts[1]
                else:
                    error(
                        "Found Jira contact, but it does not look like a project page.\n"
                        f"Expected format {JIRA_PROJECTS_URL}CLOUD\n"
                        f"Found: {parts[1]}"
                    )
                break
        teams.append(Team(team_node["name"], jira_project))

    # Add the unowned team. This is the null object pattern to make dict lookups safe.
    teams.append(Team("NO-OWNER", ""))

    return {team.name: team for team in teams}


def check_campaign_teams(services: list[Service], teams: dict[str, Team]) -> None:
    """Validate that all the teams in the campaign have connections to Jira."""
    missing_jira = set()
    for service in services:
        if not teams[service.owner].jira_project:
            missing_jira.add(service.owner)
    if missing_jira:
        teams_error = ", ".join(sorted(missing_jira))
        error(
            f"These teams do not have a Jira contact set and will be skipped when creating issues: {teams_error}\n\n"
        )


def run_opslevel_query(
    query: str, variables: dict | None = None, operation_name: str | None = None
) -> dict:
    """Run the OpsLevel query against the API."""
    headers = {
        "Authorization": f"Bearer {OPSLEVEL_APITOKEN}",
        # The campaign report is not a part of the public schema.
        # This header lets us acccess the private schema.
        # Go figure.
        "graphql-visibility": "internal",
    }

    payload: dict[Any, Any] = {"query": query}  # The type checker was being dumb here.
    if variables is not None:
        payload["variables"] = variables
    if operation_name is not None:
        payload["operationName"] = operation_name

    response = requests.post(OPSLEVEL_ENDPOINT, json=payload, headers=headers)
    if response.status_code != 200:
        fatal(f"OpsLevel request failed: {response.content.decode()}")
    return response.json()


def fetch_campaign_jira_issues(campaign: Campaign) -> dict[str, Issue]:
    """Get all the applicable Jira issues that exist for the campaign."""
    jql = f"labels in ({campaign.label}) ORDER BY key ASC"
    raw_issues = run_jira_search(jql, ["labels"])

    issues_by_service = {}
    for issue in raw_issues:
        service_name = ""
        for label in issue["fields"]["labels"]:
            if label.startswith(OPSLEVEL_JIRA_SERVICE_LABEL_PREFIX):
                service_name = label.removeprefix(OPSLEVEL_JIRA_SERVICE_LABEL_PREFIX)
        if not service_name:
            print(f"No service found for Jira issue {issue['key']}. Skipping...")
        issues_by_service[service_name] = Issue(issue["key"])

    return issues_by_service


def run_jira_search(jql: str, fields: list[str] | None = None) -> list:
    """Run a Jira search query.

    This function handles pagination automatically.
    """
    url = f"{JIRA_URL}/rest/api/3/search"

    fetching = True
    raw_issues = []
    start_at = 0
    while fetching:
        query = {"jql": jql, "startAt": start_at}
        if fields:
            query["fields"] = ",".join(fields)

        response = run_jira(url, params=query)
        data = response.json()
        raw_issues.extend(data["issues"])

        # Determine if next page is needed.
        start_at += data["maxResults"]
        if start_at >= data["total"]:
            fetching = False
    return raw_issues


def run_jira(
    url: str, params: dict | None = None, json: dict | None = None, method: str = "get"
) -> requests.Response:
    """Run a Jira API request."""
    auth = HTTPBasicAuth(JIRA_USER, JIRA_APITOKEN)
    headers = {"Accept": "application/json"}
    request_kwargs = {
        "headers": headers,
        "auth": auth,
    }
    if params is not None:
        request_kwargs["params"] = params
    if json is not None:
        request_kwargs["json"] = json

    requests_method = getattr(requests, method)
    response = requests_method(url, **request_kwargs)
    if response.status_code not in [200, 201]:
        fatal(
            f"Jira request failed: {response.status_code} {response.content.decode()}"
        )
    return response


def set_jira_metadata(teams: dict[str, Team]) -> None:
    """Set crucial Jira issue metadata for each team."""
    url = f"{JIRA_URL}/rest/api/3/issue/createmeta"

    jira_projects = sorted(
        team.jira_project for team in teams.values() if team.jira_project
    )
    params = {"projectKeys": ",".join(jira_projects)}
    response = run_jira(url, params=params)
    data = response.json()

    project_by_key = {project["key"]: project for project in data["projects"]}
    for team in teams.values():
        project = project_by_key.get(team.jira_project)
        if not project:
            continue

        team.jira_project_id = project["id"]

        issue_types_by_name = {
            issue_type["name"]: issue_type for issue_type in project["issuetypes"]
        }
        for preferred_type in ["Tech Debt", "Debt", "Task", "Story"]:
            if preferred_type in issue_types_by_name:
                team.issue_type_name = preferred_type
                team.issue_type = issue_types_by_name[preferred_type]["id"]
                break


def build_changes(
    services: list[Service], issues: dict[str, Issue], teams: dict[str, Team]
) -> list[Change]:
    """Build the changes to apply."""
    changes = []

    for service in services:
        action = Action.CREATE
        # Issue already created for this service.
        if service.name_label in issues:
            action = Action.NOOP
        # Team is missing Jira project.
        elif not teams[service.owner].jira_project:
            action = Action.NO_JIRA
        # Team doesn't have an appropriate issue type.
        elif not teams[service.owner].issue_type:
            action = Action.NO_ISSUE_TYPE

        changes.append(
            Change(
                action, service, teams[service.owner], issues.get(service.name_label)
            )
        )

    return changes


def display_table(changes: list[Change]) -> None:
    """Display the table of state and pending changes."""
    table = Table(title="Changes")
    table.add_column("Owner")
    table.add_column("Service")
    table.add_column("Issue")

    for change in changes:
        if change.action == Action.NOOP:
            issue_key = change.issue.key if change.issue else "No action"
        elif change.action == Action.NO_JIRA:
            issue_key = "[red]No Jira project set. Cannot create issue."
        elif change.action == Action.NO_ISSUE_TYPE:
            issue_key = "[red]No Jira issue type available. Cannot create issue."
        else:
            issue_key = f"[green]Create {change.team.issue_type_name} in {change.team.jira_project}"

        table.add_row(change.service.owner, change.service.name, issue_key)

    console.print(table)


def create_issues(changes: list[Change], campaign: Campaign) -> None:
    """Create the issues in Jira."""
    for change in changes:
        if not change.action == Action.CREATE:
            continue

        create_issue(change, campaign)
        # Don't hammer the API.
        time.sleep(0.1)


def create_issue(change: Change, campaign: Campaign) -> None:
    """Create an issue for the campaign."""
    print(f"Creating issue for {change.service.name}...")
    url = f"{JIRA_URL}/rest/api/3/issue"

    body = {
        "fields": {
            "summary": f"OpsLevel Campaign: {campaign.name} - {change.service.name}",
            "project": {"id": change.team.jira_project_id},
            "issuetype": {"id": change.team.issue_type},
            "labels": [campaign.label, change.service.label],
            "description": {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": campaign.brief + "\n\n" + campaign.url,
                            }
                        ],
                    },
                ],
            },
        },
        "update": {},
    }
    response = run_jira(url, json=body, method="post")
    data = response.json()
    print(f"Created {data['key']}")


def error(message: str) -> None:
    err_console.print(f"[red]{message}[/red]")


def fatal(message: str) -> NoReturn:
    error(message)
    raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
