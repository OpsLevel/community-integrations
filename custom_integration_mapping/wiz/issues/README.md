# 🧭 Wiz → OpsLevel Issues Integration Script

## Overview

This Python script — **`get_wiz_issues.py`** — automates the process of retrieving **security issues from Wiz** and sending them to **OpsLevel** via a **custom webhook integration**.

It enables continuous synchronization of Wiz issues into OpsLevel Components, providing teams with visibility into their services’ security posture directly in OpsLevel.

> 🔗 **Reference:** [OpsLevel Docs – Getting Started with Components](https://docs.opslevel.com/docs/components#getting-started-with-components)

---

## 🚀 Features

* 🔐 **Automated OAuth2 Authentication** with Wiz (Auth0 or Cognito)
* 🔁 **Cursor-based Pagination** to fetch all Wiz issues efficiently
* 📤 **OpsLevel Webhook Integration** for data ingestion
* 🧩 **Incremental Sync** — only pulls issues updated since the last run
* 🕒 **Automatic Config Update** — updates timestamp after each successful execution
* ⚠️ **Resilient Error Handling** for authentication, API, and webhook failures

---

## 🧩 Prerequisites

### 1. Python Version

* Requires **Python 3.8+**

### 2. Install Dependencies

```bash
pip install requests
```

### 3. Environment Variables

Before running the script, set the following environment variables:

| Variable                 | Description                               | Example                               |
| ------------------------ | ----------------------------------------- | ------------------------------------- |
| `WIZ_CLIENT_ID`          | Wiz API client ID                         | `abc123xyz`                           |
| `WIZ_CLIENT_SECRET`      | Wiz API client secret                     | `s3cr3tValue`                         |
| `WIZ_ENDPOINT_URL`       | Wiz GraphQL API endpoint                  | `https://api.app.wiz.io/graphql`      |
| `WIZ_TOKEN_URL`          | Wiz OAuth token endpoint                  | `https://auth.app.wiz.io/oauth/token` |
| `OPSLEVEL_WEBHOOK_UID`   | OpsLevel webhook UID                      | `abcdef123456`                        |
| `OPSLEVEL_EXTERNAL_KIND` | (Optional) External kind for webhook data | `wiz_issues`                          |

> 🧠 The script checks all required variables before execution and exits gracefully if any are missing.

---

## ⚙️ Configuration File

The script uses a JSON configuration file named `config.json` located in the same directory (`/wiz/`) to track the last successful sync timestamp.

Example:

```json
{
  "status_changed_after": "2024-01-01T00:00:00.000Z"
}
```

* The script uses this timestamp to filter for Wiz issues that have changed since the last run.
* After a successful run, it automatically updates the timestamp to the current UTC time.

---

## 🏗️ OpsLevel Setup — Create the Component Type

Before running the integration, you must create a **custom Component Type** in OpsLevel to receive the Wiz issues.

1. **Navigate to your OpsLevel admin panel**

   * Go to **Components → Manage Types**
   * Or visit: [https://app.opslevel.com/components/types](https://app.opslevel.com/components/types)

2. **Create a new Component Type**

   * Click **“New Type”**
   * Set the **Name** to something like:
     **`Wiz Issues`** or **`Wiz Security Findings`**
   * (Optional) Add a description such as:
     *“Issues imported from Wiz via webhook integration.”*

3. **Add Key Properties**
   Include fields that align with the Wiz data model:

   * `id` — string
   * `severity` — enum (Critical, High, Medium, Low)
   * `status` — string
   * `entitySnapshot.name` — string
   * `projects.name` — string
   * `updatedAt` — datetime

4. **Create a Custom Webhook Integration**

   * Go to **Integrations → Custom Webhooks**
   * Click **“New Webhook”**
   * Configure it as follows:

     * **HTTP Method:** POST
     * **Content Type:** JSON
     * **External Kind:** `wiz_issues` (must match your script’s `OPSLEVEL_EXTERNAL_KIND`)

5. **Copy the Webhook UID**

   * Copy the generated `UID` and set it as an environment variable:

     ```bash
     export OPSLEVEL_WEBHOOK_UID="your_webhook_uid_here"
     ```

6. **Validate**

   * Run the script once and confirm that Components are created/updated in OpsLevel under the new type.

> 🔗 For additional setup help, see
> [OpsLevel Docs – Getting Started with Components](https://docs.opslevel.com/docs/components#getting-started-with-components)

---

## 🧠 How It Works

1. **Authenticate** → Uses Wiz OAuth2 to obtain an API token.
2. **Load Config** → Reads `config.json` for the last sync timestamp.
3. **Query Wiz** → Executes a GraphQL query for issues (filtered and paginated).
4. **Send to OpsLevel** → Posts each page of results to your OpsLevel webhook.
5. **Update Config** → Updates `status_changed_after` to current time after success.

---

## 🧪 Example Usage

Run the script manually:

```bash
python wiz/get_wiz_issues.py
```

Example output:

```
Starting Wiz API script.
Wiz token retrieved successfully.
Filter configured to retrieve issues changed after: 2024-10-01T00:00:00.000Z
--- Fetching Page 1 (Cursor: Start) ---
Webhook: Successfully sent 50 issues to UID 'abcdef123456' with external_kind 'wiz_issues'.
-> Retrieved 50 issues on this page. Total issues processed: 50
--- Pagination Complete ---
Configuration file updated successfully. Next run will fetch issues changed after: 2025-11-04T17:10:00.000Z
```

---

## 🧰 Folder Structure

```
/wiz/
│
├── get_wiz_issues.py     # Main Wiz → OpsLevel integration script
├── config.json            # Config file (auto-updated after each run)
└── README.md              # Documentation
```

---

## 🔍 Key Functions

| Function                  | Purpose                                     |
| ------------------------- | ------------------------------------------- |
| `request_wiz_api_token()` | Retrieves OAuth token for Wiz API           |
| `get_issues_query()`      | Returns GraphQL query for Wiz issues        |
| `fetch_all_issues()`      | Handles pagination and webhook transmission |
| `send_to_webhook()`       | Sends issue data to OpsLevel                |
| `load_config()`           | Loads timestamp filter from config file     |
| `update_config()`         | Updates timestamp after success             |
| `main()`                  | Orchestrates full process                   |

---

## 🧾 License

This project is licensed under the **MIT License** (or your organization’s equivalent).
See the `LICENSE` file if included.