# Objective

To create a Custom Event Check to check against services' infrastructure resources.

# Pre-requisites

Ensure AWS infrastructure resources are tagged with the appropriate AWS tags to automatically create relationships between infrastructure resources and services inside of OpsLevel. Docs can be found here: https://docs.opslevel.com/docs/import-infrastructure-objects-via-aws#inferring-ownershiprelationships-via-aws-tags

# Bash script

[opslevel_query_services_and_related_infra.sh](opslevel_query_services_and_related_infra.sh)

Note: The bash script would need to run on a schedule to provide up-to-date information to OpsLevel.

Requirements:
* OpsLevel CLI https://github.com/OpsLevel/cli
* jq https://stedolan.github.io/jq/

# Service Infrastructure Checks

* [RDS Certificate Expiration Check](#rds-certificate-expiration-check)
* [PostgreSQL Extended Support Check](#postgresql-extended-support-check)
* [MySQL Extended Support Check](#mysql-extended-support-check)

## RDS Certificate Expiration Check 

### Objective

To create a Custom Event Check to ensure all services with related AWS RDS databases have up to date CA certificates for those RDS databases.

Why: Want to ensure that all services' RDS databases CA certificates are updated before the old certificates expire.

### Custom Event Check config

[aws-rds-certificate-expiration-check.yml](aws-rds-certificate-expiration-check.yml)

### Result Examples

Check Failed Example

![RDS Certificate Expiration Check Failed Example Image](rds_certificate_expiration_check_fail_message.png)

Check Passed Example

![RDS Certificate Expiration Check Passed Example Image](rds_certificate_expiration_check_pass_message.png)

## PostgreSQL Extended Support Check

### Objective

To create a Custom Event Check to ensure all services with related Aurora PostgreSQL databases have up to date engine versions 12 or newer.

### Custom Event Check config

[aws-postgres-extended-support-check.yml](aws-postgres-extended-support-check.yml)

### Result Examples

Check Failed Example

![PostgreSQL Extended Support Check Failed Example Image](postgres_extended_support_check_fail_message.png)

Check Passed Example

![PostgreSQL Extended Support Check Passed Example Image](postgres_extended_support_check_pass_message.png)

## MySQL Extended Support Check

### Objective

To create a Custom Event Check to ensure all services with related Aurora MySQL databases have up to date engine versions 8 or newer.

### Custom Event Check config

[aws-mysql-extended-support-check.yml](aws-mysql-extended-support-check.yml)

### Result Examples

Check Failed Example

![MySQL Extended Support Check Failed Example Image](mysql_extended_support_check_fail_message.png)

Check Passed Example

![MySQL Extended Support Check Passed Example Image](mysql_extended_support_check_pass_message.png)