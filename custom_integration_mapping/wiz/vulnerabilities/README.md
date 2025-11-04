# Wiz Vulnerability Exporter

This utility script (`get_wiz_vulnerabilities.py`) retrieves **vulnerability findings** from your Wiz environment using the Wiz GraphQL API and prepares the data for synchronization with **OpsLevel** as components of type **`wiz_vulnerability`**.

---

## 📘 Overview

The script:
- Authenticates to Wiz using OAuth2 credentials.
- Retrieves all vulnerability findings (with pagination support).
- Extracts relevant metadata fields such as `CVSSSeverity`, `remediation`, `status`, `firstDetectedAt`, etc.
- Outputs the data in structured JSON format, ready for consumption by downstream processes (such as OpsLevel sync).

This is designed to complement the existing [`get_wiz_issues.py`](./get_wiz_issues.py) integration.

---

## 🧩 Prerequisites

1. **Python 3.8+**
2. **Required packages:**
   ```bash
   pip install requests==2.28.2
````

3. **OpsLevel Component Type**

   Ensure your OpsLevel account includes the custom component type definition for Wiz vulnerabilities.
   Reference: [OpsLevel Docs — Components](https://docs.opslevel.com/docs/components#getting-started-with-components)

   Your component type should be configured as follows (already present in your environment):

   ```json
   {
     "alias": "wiz_vulnerability",
     "name": "Wiz Vulnerability",
     "icon": { "name": "PhBug", "color": "#597ef7" },
     "category": "default",
     "configuration": { "maturityEnabled": true },
     "properties": [
       { "alias": "id", "type": "string" },
       { "alias": "name", "type": "string" },
       { "alias": "cve_description", "type": "string" },
       { "alias": "cvss_severity", "type": "string" },
       { "alias": "exploitability_score", "type": "string" },
       { "alias": "impact_score", "type": "number" },
       { "alias": "first_detected_at", "type": "string" },
       { "alias": "last_detected_at", "type": "string" },
       { "alias": "resolved_at", "type": "string" },
       { "alias": "remediation", "type": "string" },
       { "alias": "vendor_severity", "type": "string" },
       { "alias": "portal_url", "type": "string" },
       { "alias": "status", "type": "string" },
       { "alias": "has_exploit", "type": "boolean" },
       { "alias": "has_cisa_kev_exploit", "type": "boolean" },
       { "alias": "fixed_version", "type": "string" },
       { "alias": "detection_method", "type": "string" },
       { "alias": "location_path", "type": "string" },
       { "alias": "resolution_reason", "type": "string" },
       { "alias": "version", "type": "string" }
     ]
   }
   ```

---

## ⚙️ Configuration

Set the following environment variables before running the script:

| Variable                          | Description                           | Example                               |
| --------------------------------- | ------------------------------------- | ------------------------------------- |
| `WIZ_CLIENT_ID`                   | Wiz API Client ID                     | `abcd1234...`                         |
| `WIZ_CLIENT_SECRET`               | Wiz API Client Secret                 | `supersecretkey`                      |
| `WIZ_API_ENDPOINT`                | Wiz API GraphQL endpoint              | `https://api.us87.app.wiz.io/graphql` |
| `WIZ_TOKEN_URL`                   | Wiz Auth Token URL                    | `https://auth.app.wiz.io/oauth/token` |
| `OPSLEVEL_API_TOKEN` *(optional)* | If integrating directly with OpsLevel | `olp_xxx...`                          |

Example (Linux/Mac):

```bash
export WIZ_CLIENT_ID="your-client-id"
export WIZ_CLIENT_SECRET="your-client-secret"
export WIZ_API_ENDPOINT="https://api.us87.app.wiz.io/graphql"
export WIZ_TOKEN_URL="https://auth.app.wiz.io/oauth/token"
```

---

## ▶️ Usage

To run the script:

```bash
python3 get_wiz_vulnerabilities.py
```

You’ll see output similar to:

```
Starting Wiz vulnerability extraction...
Authenticating to Wiz...
Fetching vulnerability findings...
✅ Extracted 512 vulnerabilities.
[
  {
    "id": "abc123",
    "name": "openssl: CVE-2024-12345",
    "severity": "HIGH",
    "score": 8.5,
    "status": "OPEN",
    "portal_url": "https://app.wiz.io/...",
    "first_detected_at": "2024-10-12T10:12:00Z",
    "vulnerable_asset_type": "VirtualMachine"
  }
]
```

---

## 🔁 Pagination and Error Handling

* The script automatically paginates through all results using `hasNextPage` and `endCursor`.
* Transient errors (HTTP 5xx, timeouts) are retried up to 3 times with exponential backoff.
* All authentication secrets are loaded securely from environment variables.

---

## 🧠 Integration with OpsLevel

Once the vulnerabilities are fetched, they can be pushed into OpsLevel using the OpsLevel GraphQL API.

For example, using a downstream sync script or job, you can create or update components of type `wiz_vulnerability`:

```python
# Example OpsLevel GraphQL mutation
mutation {
  createComponent(input: {
    name: "CVE-2024-12345"
    type: "wiz_vulnerability"
    properties: {
      id: "abc123",
      cvss_severity: "HIGH",
      remediation: "Upgrade to version 1.2.3",
      portal_url: "https://app.wiz.io/vulnerability/abc123"
    }
  }) {
    component { id name }
  }
}
```

You can learn more about component creation and updates here:
👉 [OpsLevel Components API Documentation](https://docs.opslevel.com/docs/components#getting-started-with-components)

---

## 🧰 Folder Structure

```
/wiz/
 ├── get_wiz_issues.py           # Existing Wiz issues integration
 ├── get_wiz_vulnerabilities.py  # This script
 ├── README.md                   # You are here
```

---

## 🪄 Notes

* The script outputs vulnerabilities in JSON for flexibility; you can extend it to write CSV or push directly to OpsLevel.
* Consider scheduling it as a CRON job or pipeline step (e.g., GitHub Actions, Jenkins) to run daily or weekly.
* For better security, use a secret manager (AWS Secrets Manager, Vault, etc.) for storing credentials.

---