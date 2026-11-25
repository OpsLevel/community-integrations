#!/usr/bin/env python3
"""
Create the "(Use Case) Security - GitHub Repository Risk" scorecard: risk-based checks on GitHub Repository
components (GitHub repo metadata such as data classification and external interface type feeding a rubric that
prioritizes by risk).

Filters (created if missing):
  "GitHub Repositories (active)"          type is GitHub Repository AND archived is not true   -> scorecard filter
  "GitHub Repositories - High risk (P1/P2)" active AND risk_priority is P1 or P2               -> high-risk checks

Checks (Custom Property checks on component type github_repository):
  Bronze   Data classification is set                 data_classification in public|internal|confidential|restricted
  Bronze   External interface type is set             external_interface_type in none|internal_api|public_api|public_web
  Silver   Repository has a description               repository_description is non-blank
  Silver   Not a P1 risk                              risk_priority != P1
  Gold     High risk: repository is not public        visibility != public               [High risk filter]
  Diamond  High risk: pushed to in the last 90 days   updated_date within 90 days        [High risk filter]
  Diamond  Risk priority P3 or lower                  risk_priority is P3 or P4

All predicates are jq (satisfies_jq_expression) run against the property value. A check whose filter excludes a
repo doesn't apply to it, so low-risk repos aren't held back by the high-risk controls. If the rubric has no
Diamond level, the Diamond checks go on the highest level it has.

Dry run unless --apply. Re-running is safe: filters and the scorecard are matched by name, existing checks by name.
Run create_github_repository_type.py --apply first (it creates risk_priority). Stdlib only.

Usage:
  export OPSLEVEL_API_TOKEN=...          # or OPSLEVEL_API_TOKEN=... in a .env file in the current directory
  python3 create_github_repository_scorecard.py --owner <team_alias>           # dry run
  python3 create_github_repository_scorecard.py --owner <team_alias> --apply [--disabled] [--affects-overall true|false]
"""
import argparse, json, os, sys, urllib.error, urllib.request
from pathlib import Path

TYPE_ALIAS = "github_repository"
SCORECARD_NAME = "(Use Case) Security - GitHub Repository Risk"
SCORECARD_DESCRIPTION = (
    "Risk-based standards for GitHub repositories. Each repo's **Risk Priority** (P1-P4) comes from two GitHub "
    "custom properties: **data classification** (public, internal, confidential, restricted) and **external "
    "interface type** (none, internal_api, public_api, public_web), one step higher when a public repo holds "
    "non-public data. P1 = confidential or restricted data behind a public interface.\n\n"
    "- **Bronze**: the repo is classified (both custom properties set in GitHub).\n"
    "- **Silver**: it has a description and isn't P1.\n"
    "- **Gold**: P1/P2 repos aren't public.\n"
    "- **Diamond** (Gold in rubrics with three levels): P1/P2 repos are actively maintained, and the repo's risk "
    "is P3 or lower.\n\n"
    "Archived repositories are out of scope.")
ACTIVE_FILTER = "GitHub Repositories (active)"
HIGH_RISK_FILTER = "GitHub Repositories - High risk (P1/P2)"

CLASSES = '"public", "internal", "confidential", "restricted"'
INTERFACES = '"none", "internal_api", "public_api", "public_web"'
# (name, level index, property alias, jq on the value, filter key or None, notes)
CHECKS = [
    ("Data classification is set", 1, "data_classification", f"IN({CLASSES})", None,
     "Set the `data_classification` custom property on the repo in GitHub (Settings > Custom properties): "
     "public, internal, confidential or restricted."),
    ("External interface type is set", 1, "external_interface_type", f"IN({INTERFACES})", None,
     "Set the `external_interface_type` custom property on the repo in GitHub: none, internal_api, public_api "
     "or public_web."),
    ("Repository has a description", 2, "repository_description", 'type == "string" and test("\\\\S")', None,
     "Add a description to the repository in GitHub so owners and reviewers know what it holds."),
    ("Not a P1 risk", 2, "risk_priority", '. != "P1"', None,
     "P1 means confidential or restricted data behind a public interface. Reduce exposure (internal-only "
     "interface, private repo) or confirm the classification with security."),
    ("High risk: repository is not public", 3, "visibility", '. != "public"', "high",
     "P1/P2 repos hold sensitive data or expose public interfaces; make the repository private or internal."),
    ("High risk: pushed to in the last 90 days", 4, "updated_date",
     '(sub("\\\\.[0-9]+"; "") | fromdateiso8601) > (now - 7776000)', "high",
     "Unmaintained P1/P2 repos miss security fixes. Ship a change, or archive the repo if it's no longer used."),
    ("Risk priority P3 or lower", 4, "risk_priority", '. == "P3" or . == "P4"', None,
     "Lower the repo's risk: narrow its external interface or move sensitive data out of it."),
]


class OpsLevelError(Exception):
    pass


def load_dotenv(path):
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.removeprefix("export ").split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k.startswith("OPSLEVEL_") and k not in os.environ:
                    os.environ[k] = v


class OpsLevel:
    def __init__(self, url, token):
        self.url, self.token = url, token

    def gql(self, query, variables=None):
        req = urllib.request.Request(self.url, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            raise OpsLevelError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}") from e
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise OpsLevelError(f"Could not reach OpsLevel: {e}") from e
        if data.get("errors"):
            raise OpsLevelError("GraphQL error: " + json.dumps(data["errors"])[:800])
        return data["data"]

    def mutate(self, field, input_type, input_obj, selection):
        q = f"mutation($input: {input_type}!) {{ {field}(input: $input) {{ {selection} errors {{ message path }} }} }}"
        payload = self.gql(q, {"input": input_obj}).get(field) or {}
        if payload.get("errors"):
            raise OpsLevelError(f"{field}: " + "; ".join(e["message"] for e in payload["errors"])
                                + f"\nInput: {json.dumps(input_obj)}")
        return payload

    def paged(self, query, path, variables=None):
        nodes, after, variables = [], None, dict(variables or {})
        while True:
            variables["after"] = after
            cur = self.gql(query, variables)
            for k in path:
                cur = (cur or {}).get(k)
            if not isinstance(cur, dict):
                return nodes
            nodes += [n for n in cur.get("nodes") or [] if n]
            page = cur.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                return nodes
            after = page["endCursor"]

    def fields(self, type_name):
        t = self.gql("query($n: String!) { __type(name: $n) { inputFields { name } } }", {"n": type_name})["__type"]
        return {f["name"] for f in (t or {}).get("inputFields") or []}


def require(ol, type_name, needed):
    have = ol.fields(type_name)
    if not have:
        raise OpsLevelError(f"{type_name} isn't in the API schema; nothing was changed")
    missing = set(needed) - have
    if missing:
        raise OpsLevelError(f"{type_name} lacks {sorted(missing)} (has {sorted(have)}); nothing was changed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owner", required=True, help="alias of the team that owns the scorecard and checks")
    ap.add_argument("--affects-overall", choices=["true", "false"],
                    help="set whether the scorecard affects overall levels (default: false on create, unchanged on update)")
    ap.add_argument("--disabled", action="store_true", help="create the checks disabled")
    ap.add_argument("--apply", action="store_true", help="make the changes (default: dry run)")
    ap.add_argument("--api-url", default=os.environ.get("OPSLEVEL_API_URL", "https://app.opslevel.com/graphql"))
    a = ap.parse_args()
    load_dotenv(Path.cwd() / ".env")
    token = os.environ.get("OPSLEVEL_API_TOKEN")

    print(f"Scorecard {SCORECARD_NAME!r} (owner {a.owner}), filter {ACTIVE_FILTER!r}")
    for name, lvl, alias, jq, flt, _ in CHECKS:
        print(f"  L{lvl}  {name:<58} {alias}: {jq}" + ("   [high risk]" if flt else ""))
    if not token:
        if a.apply:
            sys.exit("OPSLEVEL_API_TOKEN is not set (env or ./.env)")
        print("\nNo OPSLEVEL_API_TOKEN: showing the plan only.")
        return

    ol = OpsLevel(a.api_url, token)
    try:
        acct = ol.gql("query($t: String!) { account { team(alias: $t) { id name } "
                      "componentType(input: {alias: \"" + TYPE_ALIAS + "\"}) { id name "
                      "properties(first: 100) { nodes { id alias } } } } }", {"t": a.owner})["account"]
        team, ctype = acct.get("team"), acct.get("componentType")
        if not team:
            sys.exit(f"No team with alias {a.owner!r}.")
        if not ctype:
            sys.exit(f"No component type {TYPE_ALIAS!r}; run create_github_repository_type.py --apply first.")
        props = {p["alias"]: p["id"] for p in ctype["properties"]["nodes"]}
        missing = sorted(({c[2] for c in CHECKS} | {"archived"}) - set(props))
        if missing:
            sys.exit(f"{ctype['name']} lacks properties {missing}; run create_github_repository_type.py --apply.")
        levels = {l["index"]: l for l in ol.paged(
            "query($after: String) { account { rubric { levels(first: 100, after: $after) { nodes { id name index } "
            "pageInfo { hasNextPage endCursor } } } } }", ["account", "rubric", "levels"])}
        if not levels:
            sys.exit("The account's rubric has no levels.")
        filters = {f["name"]: f for f in ol.paged(
            "query($after: String) { account { filters(first: 100, after: $after) { nodes { id name } "
            "pageInfo { hasNextPage endCursor } } } }", ["account", "filters"])}
        cards = ol.paged("query($after: String) { account { scorecards(first: 100, after: $after) { "
                         "nodes { id name href affectsOverallServiceLevels categories(first: 10) { nodes { id name } } } "
                         "pageInfo { hasNextPage endCursor } } } }", ["account", "scorecards"])
        card = next((c for c in cards if c["name"] == SCORECARD_NAME), None)
        existing = set()
        if card:
            existing = {n["name"] for n in ol.paged(
                "query($id: ID!, $after: String) { account { scorecard(input: {id: $id}) { "
                "checks(first: 100, after: $after) { nodes { name } pageInfo { hasNextPage endCursor } } } } }",
                ["account", "scorecard", "checks"], {"id": card["id"]})}
    except OpsLevelError as e:
        sys.exit(str(e))

    def level(index):  # a check written for a level the rubric lacks goes on its highest level
        return levels[min(index, max(levels))]

    print(f"\nOwner {team['name']}; type {ctype['name']}")
    for n in (ACTIVE_FILTER, HIGH_RISK_FILTER):
        print(f"  {'=' if n in filters else '+'} filter {n}")
    print(f"  {'=' if card else '+'} scorecard {SCORECARD_NAME}" + (f"  {card.get('href', '')}" if card else ""))
    for c in CHECKS:
        print(f"    {'=' if c[0] in existing else '+'} {c[0]}  ({level(c[1])['name']})")
    if not a.apply:
        print("\nDry run only. Re-run with --apply.")
        return

    try:
        require(ol, "FilterCreateInput", {"name", "predicates", "connective"})
        require(ol, "FilterPredicateInput", {"key", "keyData", "type", "value"})
        require(ol, "CheckServicePropertyCreateInput",
                {"name", "categoryId", "levelId", "enabled", "filterId", "notes", "serviceProperty",
                 "componentType", "propertyDefinition", "propertyValuePredicate"})

        def ensure_filter(name, predicates):
            if name in filters:
                return filters[name]
            f = ol.mutate("filterCreate", "FilterCreateInput",
                          {"name": name, "connective": "and", "predicates": predicates}, "filter { id name }")["filter"]
            print(f"  + filter {name}")
            return f

        active = ensure_filter(ACTIVE_FILTER, [
            {"key": "component_type_id", "type": "equals", "value": ctype["id"]},
            {"key": "properties", "keyData": props["archived"], "type": "satisfies_jq_expression",
             "value": ". != true"},
        ])
        high = ensure_filter(HIGH_RISK_FILTER, [
            {"key": "filter_id", "type": "matches", "value": active["id"]},
            {"key": "properties", "keyData": props["risk_priority"], "type": "satisfies_jq_expression",
             "value": '. == "P1" or . == "P2"'},
        ])

        if a.affects_overall is not None:
            affects = a.affects_overall == "true"
        else:   # keep the current setting on update; off for a new scorecard
            affects = bool(card and card.get("affectsOverallServiceLevels"))
        card_input = {"name": SCORECARD_NAME, "description": SCORECARD_DESCRIPTION, "ownerId": team["id"],
                      "filterId": active["id"], "affectsOverallServiceLevels": affects}
        if card:
            res = ol.gql("mutation($sc: IdentifierInput!, $input: ScorecardInput!) { scorecardUpdate(scorecard: $sc, "
                         "input: $input) { scorecard { id href } errors { message } } }",
                         {"sc": {"id": card["id"]}, "input": card_input})["scorecardUpdate"]
            if res.get("errors"):
                raise OpsLevelError("scorecardUpdate: " + "; ".join(e["message"] for e in res["errors"]))
            print(f"  = scorecard updated  {card.get('href', '')}")
        else:
            card = ol.mutate("scorecardCreate", "ScorecardInput", card_input,
                             "scorecard { id name href categories(first: 10) { nodes { id name } } }")["scorecard"]
            print(f"  + scorecard {card['name']}  {card.get('href', '')}")
        cats = (card.get("categories") or {}).get("nodes") or ol.gql(
            "query($id: ID!) { account { scorecard(input: {id: $id}) { categories(first: 10) { nodes { id } } } } }",
            {"id": card["id"]})["account"]["scorecard"]["categories"]["nodes"]
        if not cats:
            sys.exit("The scorecard has no category to attach checks to.")
    except OpsLevelError as e:
        sys.exit(str(e))

    failed = 0
    for name, lvl, alias, jq, flt, notes in CHECKS:
        if name in existing:
            continue
        payload = {"name": name, "categoryId": cats[0]["id"], "levelId": level(lvl)["id"],
                   "enabled": not a.disabled, "notes": notes, "serviceProperty": "custom_property",
                   "componentType": {"alias": TYPE_ALIAS}, "propertyDefinition": {"alias": alias},
                   "propertyValuePredicate": {"type": "satisfies_jq_expression", "value": jq}}
        if flt:
            payload["filterId"] = high["id"]
        try:
            ol.mutate("checkServicePropertyCreate", "CheckServicePropertyCreateInput", payload, "check { id name }")
            print(f"    + {name}")
        except OpsLevelError as e:
            failed += 1
            print(f"    [ERROR] {name}: {e}")
    print(f"\nDone{' with ' + str(failed) + ' failures' if failed else ''}.  {card.get('href', '')}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
