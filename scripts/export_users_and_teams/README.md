```markdown
# OpsLevel Teams and Users Exporter

This Python script retrieves team and user data from OpsLevel using the GraphQL API and exports it to a CSV file.

## Prerequisites

* Python 3.6 or later
* `requests` library (`pip install requests`)
* OpsLevel API token (set as environment variable `OPSLEVEL_API_TOKEN`)

## Setup

1.  **Install Python Dependencies:**

    ```bash
    pip install requests
    ```

2.  **Set OpsLevel API Token:**

    Set your OpsLevel API token as an environment variable named `OPSLEVEL_API_TOKEN` and the file path as `OUTPUT_CSV_PATH`.

    * **Linux/macOS:**

        ```bash
        export OPSLEVEL_API_TOKEN="your_opslevel_api_token"
        export OUTPUT_CSV_PATH="path_to_write_file"
        ```

    * **Windows (Command Prompt):**

        ```bash
        set OPSLEVEL_API_TOKEN=your_opslevel_api_token
        set OUTPUT_CSV_PATH=path_to_write_file
        ```

    * **Windows (PowerShell):**

        ```powershell
        $env:OPSLEVEL_API_TOKEN = "your_opslevel_api_token"
        $env:OUTPUT_CSV_PATH = "path_to_write_file"
        ```

    * **Best practice:** For production systems, consider using more secure methods to store and retrieve your API token, such as environment files or secret management tools.

## Usage

1.  **Run the script:**

    ```bash
    python your_script_name.py
    ```

    Replace `your_script_name.py` with the actual name of your Python script.

2.  **Output:**

    The script will create a CSV file named `teams_and_users.csv` in the same directory as the script. This file will contain the exported team and user data.

## CSV File Structure

The `teams_and_users.csv` file will have the following columns:

* `Name`
* `Team Alias`
* `Contact Type`
* `Contact Display Name`
* `Contact Address`
* `User ID`
* `User Name`
* `User Email`
* `Membership Role`

## Script Explanation

The script consists of two main functions:

* **`get_all_teams_and_users(api_token)`:**
    * Retrieves team and user data from the OpsLevel GraphQL API.
    * Handles pagination to retrieve all data.
    * Returns a list of team data dictionaries.
* **`export_teams_and_users_to_csv(teams_data, output_csv_path="teams_and_users.csv")`:**
    * Exports the team and user data to a CSV file.
    * Handles cases where teams may not have contacts or memberships.
    * Writes the data in a structured format.
* **Main execution (`if __name__ == "__main__":`)**
    * Retrieves the API token from the environment variables.
    * Calls the `get_all_teams_and_users` function to retrieve the data.
    * Calls the `export_teams_and_users_to_csv` function to export the data to a CSV file.

## Error Handling

The script includes error handling for:

* Invalid API responses.
* API request errors.
* CSV file writing errors.
* Missing API token environment variable.

## Notes

* Ensure that you have the necessary permissions to access the OpsLevel API.
* The CSV file will overwrite any existing file with the same name.
```