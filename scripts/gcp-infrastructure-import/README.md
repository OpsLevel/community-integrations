
# Import GCP infrastructure into your OpsLevel account.

Using this GCP API call `GET https://compute.googleapis.com/compute/v1/projects/{project}/zones/{zone}/instances` as an example, we get back a list of Compute resources and save the response to a file.

This script takes two inputs:
* `TOKEN` is an OpsLevel read/write API token
* The list of infrastructure resources is read from the `instances.json` file


Executed with:

```
chmod +x gcp_infra_import.rb # done once to make the file executable
ruby gcp_infra_import.rb
```

More information on importing infrastructure resources via our GraphQL API can be found [in our documentation](https://docs.opslevel.com/docs/import-infrastructure-objects-via-api).
