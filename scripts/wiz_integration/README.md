# Wiz and OpsLevel Integration Script

## Description

This Python script (`sync_vulnerabilities.py`) integrates vulnerability data from the Wiz API with OpsLevel. It fetches vulnerability findings from Wiz, enriches them with service information from OpsLevel, and then creates or updates Code Issues and Code Issue Projects in OpsLevel.

## Features

* **Data Fetching from Wiz:**
    * Retrieves vulnerability data from the Wiz API using GraphQL queries.
    * Handles pagination to fetch all vulnerabilities.
    * Extracts relevant vulnerability information, including name, ID, CVE description, severity, and affected asset details.
* **OpsLevel Integration:**
    * Fetches service information from OpsLevel using GraphQL queries.
    * Creates or reuses Code Issue Projects in OpsLevel to organize Wiz vulnerabilities.
    * Connects Code Issue Projects to corresponding services in OpsLevel.
    * Creates Code Issues in OpsLevel for each vulnerability, linking them to the appropriate Code Issue Project.
* **Error Handling:**
    * Robust error handling for API requests, JSON parsing, and authentication.
    * Prints detailed error messages to the console for debugging.
* **Configuration:**
    * Uses environment variables for sensitive information like API tokens.

## Requirements

* Python 3.6 or later
* `requests` library (`pip install requests`)
* Environment variables:
    * `OPSLEVEL_API_TOKEN`: Your OpsLevel API token.
    * `WIZ_CLIENT_ID`: Your Wiz API client ID.
    * `WIZ_CLIENT_SECRET`: Your Wiz API client secret.

## Setup

1.  **Install Python:** Ensure you have Python 3.6 or later installed.
2.  **Install `requests`:**
    ```bash
    pip install requests
    ```
3.  **Set Environment Variables:**
    * Set the `OPSLEVEL_API_TOKEN`, `WIZ_CLIENT_ID`, and `WIZ_CLIENT_SECRET` environment variables.  You can do this in your shell's configuration file (e.g., `.bashrc`, `.zshrc`) or before running the script:
        ```bash
        export OPSLEVEL_API_TOKEN="your_opslevel_api_token"
        export WIZ_CLIENT_ID="your_wiz_client_id"
        export WIZ_CLIENT_SECRET="your_wiz_client_secret"
        ```
        For Windows:
        ```batch
        set OPSLEVEL_API_TOKEN=your_opslevel_api_token
        set WIZ_CLIENT_ID=your_wiz_client_id
        set WIZ_CLIENT_SECRET=your_wiz_client_secret
        ```

## Usage

1.  **Run the script:**
    ```bash
    python sync_vulnerabilities.py
    ```
2.  **Output:** The script will print the processed vulnerability data as JSON to the console.  It will also print the number of vulnerabilities found.  Any errors during the process will also be printed to the console.

## Script Details

### Functions

* `request_wiz_api_token(client_id, client_secret, token_url)`: Retrieves an OAuth access token from the Wiz API.
* `wiz_vulnerabilities_query()`:  Returns the GraphQL query for fetching vulnerability data from Wiz.
* `call_wiz_api(api_url, headers, query, variables)`: Executes a GraphQL query against the Wiz API.
* `ol_service_info_query()`: Returns the GraphQL query for fetching service information from OpsLevel.
* `ol_codeissue_mutation()`: Returns the GraphQL mutation for creating/updating a code issue in OpsLevel.
* `ol_codeissueproject_mutation()`: Returns the GraphQL mutation for creating/updating a code issue *project* in OpsLevel.
* `ol_x_codeissue_svc_mutation()`: Returns the GraphQL mutation for connecting a code issue project to a service.
* `call_opslevel_api(query, variables, api_token)`: Executes a GraphQL query against the OpsLevel API.
* `check_for_cip(data, name)`: Checks if a code issue project with a given name exists in a list of projects.
* `sync_vulnerabilities()`:
    * The main function that orchestrates the synchronization process.
    * Fetches vulnerability data from Wiz.
    * Fetches service data from OpsLevel.
    * Creates or updates Code Issue Projects and Code Issues in OpsLevel.
    * Handles errors and returns the processed data.

### Workflow

1.  The `sync_vulnerabilities()` function is called.
2.  It retrieves API tokens from environment variables.
3.  It fetches vulnerability data from the Wiz API.
4.  For each vulnerability, it fetches the corresponding service from OpsLevel.
5.  It checks if a Code Issue Project for Wiz vulnerabilities exists for the service.  If not, it creates one.
6.  It connects the Code Issue Project to the service in OpsLevel.
7.  It creates a Code Issue in OpsLevel for the vulnerability.
8.  The processed data is returned and printed to the console.

## Notes

* Ensure that your API tokens are correctly set in the environment variables.
* The script uses a hardcoded OpsLevel service alias (`jtoebes-echo`).  You may need to adjust this to match your OpsLevel setup.
* The script filters Wiz vulnerabilities to only process  CRITICAL vulnerabilities.  This can be changed in the `variables` definition in the `sync_vulnerabilities` function.
* The script assumes that the Wiz vulnerability data includes a tag with the key "Name" that corresponds to an OpsLevel service alias.
* The script includes error handling and will print error messages to the console.  Check the console output for details if the script does not run successfully.
