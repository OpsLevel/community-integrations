# Objective

To create a Custom Event Check to ensure all services with related AWS RDS databases have up to date CA certificates for those RDS databases.

Why: Want to ensure that all services' RDS databases CA certificates are updated before the old certificates expire.

# Pre-requisites

Ensure AWS infrastructure resources are tagged with the appropriate AWS tags to automatically create relationships between infrastructure resources and services inside of OpsLevel. Docs can be found here: https://docs.opslevel.com/docs/import-infrastructure-objects-via-aws#inferring-ownershiprelationships-via-aws-tags

# Bash script

[opslevel_query_services_and_related_infra.sh](opslevel_query_services_and_related_infra.sh)

Note: The bash script would need to run on a schedule to provide up-to-date information to OpsLevel.

Requirements:
* OpsLevel CLI https://github.com/OpsLevel/cli
* jq https://stedolan.github.io/jq/

# Custom Event Check config

[aws-rds-certificate-expiration-check.yml](aws-rds-certificate-expiration-check.yml)

# Result Examples

Check Failed Example

![Check Failed Example Image](fail_message.png)

Check Passed Example

![Check Passed Example Image](pass_message.png)