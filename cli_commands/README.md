# OpsLevel cli Library

## Overview

OpsLevel's [cli](https://docs.opslevel.com/docs/cli) interacts with the
OpsLevel API to perform CRUD actions on services, teams, or checks and
even submit deploy events.

## Community's Favorite Commands

Like many command line tools, OpsLevel's cli aims to be simple to use
while providing powerful capabilities to those that wield it.

For this we can leverage [Task](https://taskfile.dev).

### Task

Install task [here](https://taskfile.dev/installation)

View available tasks with `task --list`

## OpsLevel CLI setup with Task

Streamline OpsLevel CLI setup with this command:

```sh
# From this directory
task install-cli
```

This task uses `brew` to install the `cli` and `jq`.
