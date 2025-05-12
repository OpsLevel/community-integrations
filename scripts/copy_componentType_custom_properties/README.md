# Copy Custom Properties from one Component Type to another Component Type

This script is designed to copy custom properties from one Component Type to another Component Type in your OpsLevel account.

Prequisites:

- The property definition must be defined on a component type to copy from.

Requirements:

- Python 3.10.10 or higher
- `requests` library is installed

To run this:

1. Add your api token to an `OPSLEVEL_API_TOKEN` environment variable
2. Execute the command below
3. Choose the Component Type to copy from by entering the integer value in the list.
4. Choose the property definition to copy from by entering the integer value in the list or press `a` to select all.
5. Choose the Component Type to copy to by entering the integer value in the list.

```bash
python ./copy_componentType_custom_properties.py
```
