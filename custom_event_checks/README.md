# Custom Event Checks Library

## Overview
OpsLevel's [Custom Event Checks](https://docs.opslevel.com/docs/custom-event-checks) accept arbitrary JSON payloads from any source to create custom, data-driven checks.

The JSON payloads are:
* parsed and mapped to the corresponding Services in your OpsLevel account
* evaluated against your Custom Event Check's conditions to determine if a Service has passed or failed the Check


These Custom Event Check configs are in YAML format. Existing Custom Event Checks can be exported to YAML from the OpsLevel GUI or with our [CLI](https://docs.opslevel.com/docs/cli).
* On the service maturity rubric, select the `...` menu on the desired check and then select `Download Config`
* Using our CLI run `opslevel get check <CHECK_ID> -o yaml`
