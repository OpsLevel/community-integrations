# Wiz → OpsLevel

OpsLevel now ships a [first-class Wiz integration](https://docs.opslevel.com/docs/wiz-integration).
The examples here are legacy, or for cases that need additional customization.

| Example | Pattern | Use it when |
| :------ | :------ | :---------- |
| [`pull_configuration/`](pull_configuration/) | **Pull** — OpsLevel polls the Wiz GraphQL API on a schedule, configured entirely in YAML | Your have an unusual Wiz tenant (e.g. Wiz for Gov, AWS GovCloud, or an older Auth0 tenant) or you want more control over how the data is represented in OpsLevel |
| [`issues/`](issues/) | **Push** — a Python script you run yourself, POSTing issues to an OpsLevel custom webhook | You want to run the sync from your own infrastructure, filter or reshape the data before it ever reaches OpsLevel, or drive it from an existing job scheduler |
