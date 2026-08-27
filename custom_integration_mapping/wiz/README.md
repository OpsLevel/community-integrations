# Wiz → OpsLevel

Two ways to get your Wiz security issues into your OpsLevel catalog.

**Most accounts should not need either of these.** OpsLevel ships a
[first-class Wiz integration](https://docs.opslevel.com/docs/wiz) — add it from
**Integrations → + New Integration → Wiz**, give it your Wiz API endpoint URL and
a service account's client ID and secret, and you're done. The examples here are
for the cases the built-in integration doesn't cover.

| Example | Pattern | Use it when |
| :------ | :------ | :---------- |
| [`pull_configuration/`](pull_configuration/) | **Pull** — OpsLevel polls the Wiz GraphQL API on a schedule, configured entirely in YAML | Your Wiz tenant authenticates somewhere other than Wiz's commercial endpoint (Wiz for Gov, AWS GovCloud, or an older Auth0 tenant), so the built-in integration can't reach it |
| [`issues/`](issues/) | **Push** — a Python script you run yourself, POSTing issues to an OpsLevel custom webhook | You want to run the sync from your own infrastructure, filter or reshape the data before it reaches OpsLevel, or drive it from an existing job scheduler |

The pull example is the closer match to the built-in integration: it uses the
same extract and transform definitions OpsLevel itself runs, published straight
out of the product, so you get the same components, tags and properties without
writing any of the mapping by hand.
