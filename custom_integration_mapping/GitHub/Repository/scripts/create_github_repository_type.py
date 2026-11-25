#!/usr/bin/env python3
"""
Create (or update) the "GitHub Repository" component type (alias `github_repository`) and its custom properties
through the OpsLevel GraphQL API. ../transform_definition.yaml writes every one of these properties.

Dry run unless --apply. Re-running is safe:
  - type missing  -> componentTypeCreate with every property
  - type present  -> componentTypeUpdate sending the FULL property list (existing aliases are updated in place,
                     missing ones are added; nothing is removed)

Usage:
  export OPSLEVEL_API_TOKEN=...              # or OPSLEVEL_API_TOKEN=... in a .env file in the current directory
  python3 create_github_repository_type.py           # dry run
  python3 create_github_repository_type.py --apply

Input field names are checked against the API schema (introspection) before anything is changed. Stdlib only.
"""
import argparse, json, os, sys, urllib.error, urllib.request
from pathlib import Path

TYPE = {
    "name": "GitHub Repository",
    "alias": "github_repository",
    "description": ("One component per GitHub repository, created and kept up to date by the GitHub Repositories "
                    "custom integration (repo metadata, visibility, dates), tagged with its risk classification for "
                    "risk-based checks."),
}

STR, BOOL, DATE = {"type": "string"}, {"type": "boolean"}, {"type": "string", "format": "date-time"}

# (name, alias, schema, description, source)
#   source "integration": set by the custom integration -> not in opslevel.yml, not editable in the UI
#   source "api":         set by automation/API later   -> not in opslevel.yml, editable in the UI
#   source "manual":      set by people                 -> opslevel.yml and UI
# Every property below is written by the custom integration. Add "api" or "manual" properties here if something
# else will populate them (e.g. CodeQL status, an owner override). Every property needs a non-empty description.
PROPERTIES = [
    ("Age(in months)", "age_in_months", {"type": "integer", "minimum": 0},
     "Whole calendar months since repo creation, recomputed each run", "integration"),
    ("archived", "archived", BOOL, "Boolean that shows whether a repository is archived or not", "integration"),
    ("Creation Date", "creation_date", DATE, "Date the repo was Created in Github", "integration"),
    ("empty", "empty", BOOL,
     "Marks repositories detected as empty by Github sync. Defaults to false when value is missing.", "integration"),
    ("Github ID", "github_id", {"type": "integer", "minimum": 0}, "The Github ID of the repository", "integration"),
    ("Repository Description", "repository_description", STR,
     "The description of the repository as listed in Github.", "integration"),
    ("Repository Name", "repository_name", STR, "The full name of the repository in github", "integration"),
    ("Updated Date", "updated_date", DATE,
     "- date the repo last had changes\n- this would be useful for finding out which repos might be stale or no "
     "longer used", "integration"),
    ("Visibility", "visibility", {"type": "string", "pattern": "^[A-Za-z]+$"},
     "The ability for people in and out of the organization to be able to view the repository", "integration"),
    ("GitHub Topics", "github_topics", {"type": "array", "items": STR, "uniqueItems": True},
     "Topics set on the repository in GitHub.", "integration"),
]

INTROSPECT = "query($n: String!) { __type(name: $n) { inputFields { name type { name kind ofType { name } } } } }"
ENUM = "query($n: String!) { __type(name: $n) { enumValues { name } } }"


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

    def input_fields(self, type_name):
        t = self.gql(INTROSPECT, {"n": type_name})["__type"]
        if not t:
            raise OpsLevelError(f"{type_name}: type not found in the API schema")
        return {f["name"]: (f["type"].get("name") or (f["type"].get("ofType") or {}).get("name"))
                for f in t["inputFields"] or []}


def property_inputs(ol):
    fields = ol.input_fields("ComponentTypePropertyDefinitionInput")
    missing = {"name", "alias", "description", "schema"} - set(fields)
    if missing:
        raise OpsLevelError(f"ComponentTypePropertyDefinitionInput lacks {sorted(missing)}; nothing was changed")
    # "Modifiable on the UI" toggle: lockedStatus enum, if the API exposes it
    locked, unlocked = None, None
    if "lockedStatus" in fields and fields["lockedStatus"]:
        vals = [v["name"] for v in (ol.gql(ENUM, {"n": fields["lockedStatus"]})["__type"] or {}).get("enumValues") or []]
        unlocked = next((v for v in vals if v.lower() == "unlocked"), None)
        locked = next((v for v in vals if v != unlocked and "lock" in v.lower()), None)
    out = []
    for name, alias, schema, desc, source in PROPERTIES:
        p = {"name": name, "alias": alias, "description": desc, "schema": json.dumps(schema)}
        if "propertyDisplayStatus" in fields:
            p["propertyDisplayStatus"] = "visible"
        if "allowedInConfigFiles" in fields:
            p["allowedInConfigFiles"] = source == "manual"
        if locked and unlocked:
            p["lockedStatus"] = locked if source == "integration" else unlocked
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true", help="make the changes (default: dry run)")
    ap.add_argument("--api-url", default=os.environ.get("OPSLEVEL_API_URL", "https://app.opslevel.com/graphql"))
    a = ap.parse_args()
    load_dotenv(Path.cwd() / ".env")
    token = os.environ.get("OPSLEVEL_API_TOKEN")

    print(f"Component type {TYPE['name']} ({TYPE['alias']}), {len(PROPERTIES)} properties:")
    for name, alias, schema, _, source in PROPERTIES:
        print(f"  {alias:<36} {source:<11} {json.dumps(schema)}")
    if not token:
        if a.apply:
            sys.exit("OPSLEVEL_API_TOKEN is not set (env or ./.env)")
        print("\nNo OPSLEVEL_API_TOKEN: showing the plan only.")
        return

    ol = OpsLevel(a.api_url, token)
    try:
        types = ol.gql("{ account { componentTypes(first: 200) { nodes { id name aliases "
                       "properties(first: 100) { nodes { alias } } } } } }")["account"]["componentTypes"]["nodes"]
        ctype = next((t for t in types if TYPE["alias"] in (t.get("aliases") or [])), None)
        wanted = [p[1] for p in PROPERTIES]
        if ctype:
            have = {n["alias"] for n in ctype["properties"]["nodes"]}
            extra = sorted(have - set(wanted))
            print(f"\n= type exists; will add {len(set(wanted) - have)} and update {len(have & set(wanted))} properties")
            if extra:
                print(f"! properties not in this script: {', '.join(extra)}. --apply stops until they're added to "
                      "PROPERTIES (sending the property list could otherwise remove them).")
        else:
            print("\n+ create type with all properties")
        if not a.apply:
            print("\nDry run only. Re-run with --apply.")
            return

        props = property_inputs(ol)
        sel = "componentType { id name properties(first: 100) { nodes { alias } } } errors { message path }"
        if ctype:
            if extra:  # never drop properties someone added by hand
                sys.exit("The type has properties this script doesn't know; add them to PROPERTIES first: "
                         + ", ".join(extra))
            res = ol.gql("mutation($id: IdentifierInput!, $input: ComponentTypeInput!) "
                         f"{{ componentTypeUpdate(componentType: $id, input: $input) {{ {sel} }} }}",
                         {"id": {"alias": TYPE["alias"]}, "input": {"description": TYPE["description"],
                                                                     "properties": props}})["componentTypeUpdate"]
        else:
            res = ol.gql(f"mutation($input: ComponentTypeInput!) {{ componentTypeCreate(input: $input) {{ {sel} }} }}",
                         {"input": {**TYPE, "properties": props}})["componentTypeCreate"]
        if res.get("errors"):
            sys.exit("; ".join(f"{e['message']} ({e.get('path')})" for e in res["errors"]))
        got = {n["alias"] for n in res["componentType"]["properties"]["nodes"]}
        print(f"Done: {res['componentType']['name']} has {len(got)} properties"
              + (f"; MISSING {sorted(set(wanted) - got)}" if set(wanted) - got else ""))
    except OpsLevelError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
