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
* jq https://stedolan.github.io/jq/
* yq https://github.com/mikefarah/yq
* Ensure that the domains only have 1 alias defined (the alias should be indicated as locked in the UI)

# Steps and commands

1. Backup systems and domains, replace <date-time> with the current date and time for uniqueness. e.g. systems_20241022-1636.json

```
opslevel list systems -o json > systems_<date-time>.json
opslevel list domains -o json > domains_<date-time>.json
```

2.  Delete systems

```
cat systems_<date-time>.json | jq '.[] | .Id' | xargs -n1 opslevel delete system
```

3. Delete domains

```
cat domains_<date-time>.json | jq '.[] | .Id' | xargs -n1 opslevel delete domain
```

4. Create domains into systems, preserve name, preserve owner, preserve description

**On MacOS**

```
cat domains_<date-time>.json | jq -c 'map({name: .Name, ownerId: .Owner.OnTeam.id, description: .Description}) | .[]' | while read -r item; do
  echo "$item" | yq | opslevel create system
done
```

**On Linux**

```
cat domains_<date-time>.json | jq -c 'map({name: .Name, ownerId: .Owner.OnTeam.id, description: .Description}) | .[]' | while read -r item; do
  echo "$item" | yq eval | opslevel create system
done
```

5. Create systems into services, preserve name, preserve owner, preserve description, preserve link to domain (now a system)

**On MacOS**

```
cat systems_<date-time>.json| jq -c 'map({name: .Name, owner: {id: .Owner.OnTeam.id}, description: .Description, parent: {alias: .Parent.Aliases[0]}}) | .[]' | while read -r item; do
  echo "$item" | yq | opslevel create service
done
```

**On Linux**

```
cat systems_<date-time>.json| jq -c 'map({name: .Name, owner: {id: .Owner.OnTeam.id}, description: .Description, parent: {alias: .Parent.Aliases[0]}}) | .[]' | while read -r item; do
  echo "$item" | yq eval | opslevel create service
done
```

Optionally, you can add additional data if needed. For example, adding prefix "SEARCH-" to the name.

**On MacOS**

```
cat systems_<date-time>.json| jq -c 'map({name: ("SEARCH-" + .Name), owner: {id: .Owner.OnTeam.id}, description: .Description, parent: {alias: .Parent.Aliases[0]}}) | .[]' | while read -r item; do
  echo "$item" | yq | opslevel create service
done
```

**On Linux**

```
cat systems_<date-time>.json| jq -c 'map({name: ("SEARCH-" + .Name), owner: {id: .Owner.OnTeam.id}, description: .Description, parent: {alias: .Parent.Aliases[0]}}) | .[]' | while read -r item; do
  echo "$item" | yq eval | opslevel create service
done
```