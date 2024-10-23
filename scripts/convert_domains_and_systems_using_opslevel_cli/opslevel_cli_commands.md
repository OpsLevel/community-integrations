# Convert Domains and Systems using the opslevel-cli

The opslevel-cli commands and steps below can be used to convert domains into systems, and systems into services.

Notes on converting domains into systems:
* Domain names will be preserved
* Owner will be preserved
* Description will be preserved

Notes on converting Systems into services:
* System names will be prefixed with "SEARCH-"
* Owner will be preserved
* Description will be preserved
* Link to new system (previously domain) will be preserved

# Requirements

* opslevel-cli installed https://github.com/OpsLevel/cli
* Ensure that the domains and systems only have 1 alias defined (the alias should be indicated as locked in the UI)

# Steps and commands

1. Backup systems and domains

```
opslevel list systems -o json > systems_<filename>.json
opslevel list domains -o json > domains_<filename>.json
```

2.  Delete systems

```
cat systems_<filename>.json | jq '.[] | .Id' | xargs -n1 opslevel delete system
```

3. Delete domains

```
cat domains_<filename>.json | jq '.[] | .Id' | xargs -n1 opslevel delete domain
```

4. Create domains into systems, preserve name, preserve owner, preserve description

```
cat domains_<filename>.json | jq -c 'map({name: .Name, owner: {id: .Owner.OnTeam.id}, description: .Description}) | .[]' | while read -r item; do
  echo "$item" | yq | opslevel create system
done
```

5. Create systems into services, add prefix "SEARCH-" to the name, preserve owner, preserve description, preserve link to domain (now a system)

```
cat systems_<filename>.json| jq -c 'map({name: ("SEARCH-" + .Name), owner: {id: .Owner.OnTeam.id}, description: .Description, parent: {alias: .Parent.Aliases[0]}}) | .[]' | while read -r item; do
  echo "$item" | yq | opslevel create service
done
```