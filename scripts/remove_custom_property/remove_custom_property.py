import os, requests # os: read the API token from your environment; requests: HTTP calls

# ---- Configuration: the only lines you normally touch -----------------------
TOKEN  = os.environ["OPSLEVEL_API_TOKEN"] # your OpsLevel API token (set it in the shell, not in the file)
URL    = "https://app.opslevel.com/graphql" # OpsLevel's single GraphQL endpoint
PROP   = "name"  # the property to remove (matched by alias OR display name)
PREFIX = "aws_"   # which component types count as "infra": those whose alias starts with this
APPLY  = True    # safety switch: False = dry run (prints only), True = actually deletes

def gql(q, v=None):
    r = requests.post(URL, headers={"Authorization": f"Bearer {TOKEN}"}, json={"query": q, "variables": v or {}})
    r.raise_for_status(); d = r.json() # raise if HTTP failed (401 bad token, 5xx, etc.)
    if d.get("errors"): raise SystemExit(d["errors"]) # GraphQL can return 200 OK but still carry errors
    return d["data"]  # the useful payload lives under "data"

def infra_types():
    """Return every component type whose alias starts with PREFIX (your 21 infra types)."""
    # componentTypes returns ALL types (Services, Teams, infra...) so we filter ourselves.
    # It's paginated (max 100 per page), so we loop, passing the previous page's cursor.

    q = "query($a:String){account{componentTypes(first:100,after:$a){nodes{id name aliases} pageInfo{hasNextPage endCursor}}}}"

    out, after = [], None # accumulated matches, and the paging cursor (None = first page)
    while True:
        c = gql(q, {"a": after})["account"]["componentTypes"]

        # keep only nodes where any alias begins with PREFIX
        out += [n for n in c["nodes"] if any((a or "").startswith(PREFIX) for a in (n["aliases"] or []))]

        if not c["pageInfo"]["hasNextPage"]: return out # no more pages -> done

        after = c["pageInfo"]["endCursor"] # otherwise fetch the next page

def delete_name():
    """For each infra type: find the PROP definition and delete it (or preview it)."""
    # PQ: given one component type, list its property definitions (id + aliases + name).
    PQ  = "query($i:IdentifierInput!){account{componentType(input:$i){properties(first:100){nodes{id aliases name}}}}}"

    # DEL: delete one property definition by its id; returns any per-item errors.
    DEL = "mutation($r:IdentifierInput!){propertyDefinitionDelete(resource:$r){errors{message}}}"
    types = infra_types()
    print(f"{len(types)} infra type(s) matched prefix '{PREFIX}' (expecting 21)")
    for t in types:
        alias = (t["aliases"] or [t["name"]])[0]  # a readable label for logging

        # Each component type has its OWN copy of the property, so we look it up per type by id.
        props = gql(PQ, {"i": {"id": t["id"]}})["account"]["componentType"]["properties"]["nodes"]

        # find the property whose alias matches PROP exactly, or whose name matches case-insensitively
        hit = next((p for p in props if PROP in (p["aliases"] or []) or p["name"].lower() == PROP.lower()), None)

        if not hit: print(f"{alias}: no '{PROP}'"); continue  # this type doesn't have the property
        if not APPLY: print(f"{alias}: would delete {hit['id']}"); continue  # dry run: show what *would* happen, change nothing

        # live delete: send the mutation, then read back any errors for THIS type
        errs = gql(DEL, {"r": {"id": hit["id"]}})["propertyDefinitionDelete"]["errors"]
        print(f"{alias}: {'FAILED ' + str(errs) if errs else 'deleted'}")

delete_name() # run it
