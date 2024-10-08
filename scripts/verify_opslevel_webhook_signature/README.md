# Verify OpsLevel Webhook Signature

# Overview

OpsLevel webhooks can be configured to be sent with a signature that the 
destination server can use to verify that the event came from the OpsLevel 
server platform and not a third party or malicious system.

More on our OpsLevel docs here: https://docs.opslevel.com/docs/webhook-signatures

Several examples on how to implement this can be found here.

## Example Code Written in Python and Flask

[verify_opslevel_webhook_signature.py](./python/verify_opslevel_webhook_signature.py)

