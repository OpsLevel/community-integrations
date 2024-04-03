# Convert Tags to Custom Properties

This script is designed to convert service tags to custom properties in your OpsLevel account. It is assumed that the tag key and the property definition key are the same. Tags are kept on services in case converting to a property definition does not work as expected.

The script can be updated to convert tags to your custom properties' definitions as needed.

Prequisites:

- The property definition must be defined first in your OpsLevel account. Only Admins have permission to create property definitions.
- The property definition key matches the tag key.

Requirements:

- Python 3.10.10
- `requests` library is installed

To run this:

1. Add your api token to an `OPSLEVEL_API_TOKEN` environment variable
2. Execute the command below and choose which property you want to convert by entering the integer value in the list.

```bash
python ./convert_tags_to_custom_properties.py
```