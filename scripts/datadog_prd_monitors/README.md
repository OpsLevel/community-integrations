# Attach Only Production Datadog Monitors to Components

OpsLevel attaches a Datadog monitor to a component when the monitor has a tag such as `service:shopping-cart` and `shopping-cart` is one of the component's aliases. It only looks at that one tag key, so a staging monitor tagged `service:shopping-cart` and `env:stg` is attached to the same component as the production monitor tagged `service:shopping-cart` and `env:prd`. Disconnecting the staging monitor in the UI doesn't last, because the next sync attaches it again.

Leaving OpsLevel's webhook (`@webhook-OpsLevel` by default) out of the staging monitor's message doesn't help either. While **Set Webhooks On Monitors** is on, OpsLevel adds the webhook to every monitor it attaches.

This script attaches monitors based on two tags instead of one, for example `service:shopping-cart` **and** `env:prd`, or you can modify it to fit your needs.

For every Datadog monitor in OpsLevel, it:

- attaches monitors tagged `env:prd` to the component named in each `service:` tag
- detaches monitors tagged with any other env, such as `env:stg`
- leaves monitors with no `env` tag alone, unless you use `--reset`

It never touches:

- alert sources from other integrations, such as PagerDuty or Opsgenie
- the monitors themselves in Datadog (OpsLevel may still add or remove its webhook, see [How it works](#how-it-works))

It never attaches monitors tagged `env:prd` that have no `service:` tag, because there's no component to attach them to.

Detaching a monitor can't be undone automatically, but you can attach it again by hand at any time with **Connect Alert Source** on the component's **Operations** tab.

## Requirements

- Python 3
- The `requests` library installed
- A read-write API token, which must be created by an admin
- A Datadog integration in OpsLevel

## Before you run this

The script replaces OpsLevel's automatic matching, so turn that off first. Otherwise the next sync attaches the staging monitors again.

1. In OpsLevel, go to **Integrations** and open your Datadog integration.
2. Under **Component Tag Keys**, click **Edit**.
3. Replace `service` with a key that none of your monitors use, for example `opslevel-alert-source`. The list can't be empty, so a placeholder key is needed.
4. Save.

OpsLevel still syncs your monitors from Datadog, but it no longer attaches any of them to components. The script does that instead.

## To run this

1. Add your API token to an `OPSLEVEL_API_TOKEN` environment variable.
2. If you are on self-hosted OpsLevel, add your GraphQL endpoint to an `OPSLEVEL_ENDPOINT` environment variable, for example `https://<your-opslevel-host>/graphql`.
3. Run the commands below.

## sync_datadog_prd_monitors.py

The script `sync_datadog_prd_monitors.py` goes through every Datadog monitor in the account and lists the links it would add or remove. By default it runs as a dry run and doesn't change anything:

```bash
python ./sync_datadog_prd_monitors.py
```

Example output:

```
Found 10 Datadog monitor(s): 1 link(s) to remove, 3 link(s) to add
[dry-run] Would unlink: Checkout latency - stg from shopping-cart (env stg)
[dry-run] Would link: Payments errors - prd to payments
[dry-run] Would link: Shared DB - prd to payments
[dry-run] Would link: Shared DB - prd to shopping-cart
Dry run complete; nothing was changed. Re-run with --apply to make the changes above.
```

Once you've reviewed the list, run the script with `--apply` to make the changes:

```bash
python ./sync_datadog_prd_monitors.py --apply
```

If a change fails, for example because no component has the alias in the monitor's `service:` tag, the script logs the error and continues with the rest. The script doesn't retry, so if OpsLevel rate limits the API token on a large account, some changes are reported as failed. Run the same command again to finish them.

### First run: `--reset`

Monitors that OpsLevel attached before you changed the tag key stay attached, including monitors with no `env` tag. To start from a clean slate, run the script once with `--reset`. It removes every link except an `env:prd` monitor's link to a component named in its own `service:` tags, then adds any of those links that are missing. Correct links are left in place, so they aren't removed and added back:

```bash
python ./sync_datadog_prd_monitors.py --reset
python ./sync_datadog_prd_monitors.py --reset --apply
```

`--reset` also detaches monitors that someone attached by hand, unless the monitor is tagged `env:prd` and attached to a component in its own `service:` tags. Review the dry run before applying it.

### Keep it running

With automatic matching turned off, new production monitors aren't attached until the script runs again. Run the script on a schedule, for example hourly from cron or a CI job, **without** `--reset`:

```bash
python ./sync_datadog_prd_monitors.py --apply
```

It only changes what's out of date, so it's safe to run as often as you like. Don't schedule `--reset`: it would also detach any monitor someone attaches by hand.

OpsLevel syncs Datadog monitors about once an hour. To pick up new monitors sooner, click **Update Monitors** on the Datadog integration page (at most once an hour), wait a few minutes, then run the script.

### Different tags

If your production env tag isn't `prd`, pass it with `--env`:

```bash
python ./sync_datadog_prd_monitors.py --env production
```

If your monitors name the component with a tag key other than `service`, pass it with `--service-key`:

```bash
python ./sync_datadog_prd_monitors.py --service-key app
```

Tag values are matched exactly, including case. `env:PRD` doesn't match `--env prd`, and `service:Shopping-Cart` isn't treated as the same component as an existing link to `shopping-cart`.

## How it works

| Monitor's tags | What the script does |
|---|---|
| `service:X` + `env:prd` | Attaches it to component `X` |
| `service:X` + `service:Y` + `env:prd` | Attaches it to both `X` and `Y` |
| `service:X` + `env:prd` + `env:stg` | Treats it as production and attaches it to `X` |
| `service:X` + any other env | Detaches it from every component |
| `service:X` with no `env` tag | Leaves it as it is, except with `--reset`, which detaches it |
| `service:X` + `env:prd`, also attached to `Y` | Leaves the `Y` link, except with `--reset`, which detaches it from `Y` |
| `env:prd` with no `service:` tag | Never attaches it; with `--reset`, detaches it from anything it's attached to |

While **Set Webhooks On Monitors** is on in the Datadog integration, OpsLevel adds its webhook to a monitor's message when the monitor is attached, and removes it when the monitor is detached from its last component. The webhook is the integration's **Datadog Notification Channel**, `@webhook-OpsLevel` by default. The script's changes trigger this the same way changes in the UI do.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success, including dry runs and runs with nothing to change |
| 1 | One or more links failed to change, or nothing was changed because of a setup problem, for example a missing token or a failed API request while listing monitors |
| 2 | Nothing was changed because of an invalid argument, for example an unknown flag or `--env` without a value |
