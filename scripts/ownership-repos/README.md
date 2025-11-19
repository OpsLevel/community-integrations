# OpsLevel Repository Ownership Updater

This Python script automates the process of updating repository ownership in OpsLevel. It reads a list of repositories and their target owners (squads) from a JSON file, checks if they exist in OpsLevel, creates the teams if they are missing, and assigns ownership.

## Features

  * **Bulk Processing:** Efficiently fetches all existing repositories from OpsLevel at the start to minimize API calls.
  * **Automatic Team Creation:** If a target team (squad) does not exist in OpsLevel, the script creates it automatically before assigning ownership.
  * **Dry Run Mode:** Simulate the process to see which repositories would be updated, which teams would be created, and which repositories are missing, without making actual changes.
  * **Service Syncing:** When updating ownership, `syncLinkedServices` is set to `true`, ensuring services linked to the repository also inherit the new owner.
  * **Execution Summary:** Provides a detailed report at the end of execution listing found/missing repos and found/created teams.

## Prerequisites

  * Python 3.x
  * An OpsLevel API Token
  * The `requests` library

## Installation

1.  **Install Dependencies:**
    The script requires the `requests` library to handle HTTP requests.

    ```bash
    pip install requests
    ```

2.  **Prepare the Input File:**
    Create a file named `repos.json` in the same directory as the script. The structure should be:

    ```json
    {
      "repositories": [
        {
          "name": "activity-data-downloader",
          "squadName": "jarvis"
        },
        {
          "name": "another-repo-name",
          "squadName": "platform-engineering"
        }
      ]
    }
    ```

      * **name:** Must match the repository name in OpsLevel exactly.
      * **squadName:** The name of the team you want to own the repo.

## Configuration

The script requires your OpsLevel API Token to be set as an environment variable for security.

**Mac / Linux:**

```bash
export OPSLEVEL_API_TOKEN="your_api_token_here"
```

**Windows (PowerShell):**

```powershell
$env:OPSLEVEL_API_TOKEN="your_api_token_here"
```

**Windows (CMD):**

```cmd
set OPSLEVEL_API_TOKEN=your_api_token_here
```

## Usage

### 1\. Dry Run (Recommended First Step)

Run the script with the `--dry-run` flag to simulate the changes. This will print a summary of what *would* happen (e.g., which teams would be created) without modifying data in OpsLevel.

```bash
python udpate-repo-ownership.py --dry-run
```

### 2\. Live Update

Once you are satisfied with the dry run results, remove the flag to perform the actual updates.

```bash
python udpate-repo-ownership.py
```

## Script Workflow

1.  **Validation:** Checks if `OPSLEVEL_API_TOKEN` is present.
2.  **Prefetch:** Downloads a list of **all** repository IDs and names from OpsLevel (handling pagination) to create a local lookup map.
3.  **Processing:** Iterates through your `repos.json` file:
      * **Repo Check:** Checks if the repo name exists in the downloaded OpsLevel map.
      * **Team Check:** Searches OpsLevel for the `squadName`.
      * **Team Creation:** If the team is not found, it creates the team immediately (unless in Dry Run mode).
      * **Update:** Updates the repository owner to the Team ID.
4.  **Reporting:** specific lists are printed to the console:
      * Repos Found / Not Found
      * Teams Found / Created

## Troubleshooting

  * **"Repository not found":** Ensure the `name` in your JSON matches the OpsLevel repository name exactly.
  * **"Error: OPSLEVEL\_API\_TOKEN environment variable is not set":** Ensure you ran the export command in the same terminal window before running the Python script.
  * **Permission Errors:** Ensure your API Token has write permissions for Teams and Repositories.