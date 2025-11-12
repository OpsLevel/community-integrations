# OpsLevel Custom Integration Mapping for Kyverno Issues

## Introduction: Understanding Kyverno and Policy Reporter

**Kyverno** (Greek for “govern”) is a **cloud native policy engine**. It was originally built for Kubernetes but now provides a unified policy language that can be used outside of Kubernetes clusters. Kyverno allows platform engineers to **automate security, compliance, and best practices validation** to provide secure self-service capabilities to application teams.

Kyverno policies are defined as **YAML-based declarative Kubernetes resources**, meaning platform engineers do not need to learn a new language. Kyverno can enforce policies using the Kubernetes admission controller, CLI-based scanning, and at runtime. Policy results are reported using the **open reporting format** standardized by the CNCF Policy Working Group.

When Kyverno policies are run in `audit` mode, they generate `PolicyReports`. Policy Reporter was created to improve the **visibility and observability** of these validation policy results. Policy Reporter addresses the disadvantage that PolicyReport results can be spread across multiple namespaces or make it difficult to check for new violations. It achieves this by providing features like sending new violations to different clients (e.g., Slack, Loki, or Elasticsearch) via webhooks.

## Prerequisites

1.  An active OpsLevel account with permissions to define Component Types and Custom Integrations.
2.  A running Kyverno installation within a Kubernetes cluster.
3.  Kyverno Policy Reporter installed in the cluster, with access to its configuration file (e.g., `values.yaml`).

## Step 1: Create the Custom Component Type: Kyverno Issue

To track policy violations in the OpsLevel Software Catalog, you must first define a Custom Component Type.

1.  Navigate to **Settings > Component Types** in the OpsLevel UI.
2.  Select **+ New Component Type**.
3.  Define the Component Type:
    *   **Display Name:** Kyverno Issue (as requested)
    *   **Identifier:** Choose a unique identifier (e.g., `kyverno_issue`).
    *   **Description:** Provide context for this component type.
4.  Once the Component Type is created, define the following **Custom Properties**. These properties are necessary to receive the data pushed from the Policy Reporter webhook via the custom integration mapping:

| OpsLevel Property Name | Data Type (Example: Text/String) | Mapped from Kyverno Data (JQ Path) | Purpose |
| :--- | :--- | :--- | :--- |
| **Category** | Text/String | `.category` | Policy category. |
| **Message** (Content) | N/A | (Captured in Summary) | Raw policy message content is mapped to the `Summary` property. |
| **Namespace** | Text/String | `.resource.namespace` | Kubernetes Namespace where the violation occurred. |
| **Priority** | Text/String | `.priority` | Priority of the violation. |
| **Resource Name** | Text/String | `.resource.name` | Name of the Kubernetes resource that failed the policy. |
| **Severity** | Text/String | `.severity` | Severity level of the violation. |
| **Status** | Text/String | `.status` | Result status (e.g., Fail). |
| **Summary** | Text/String | `.message` | Violation message mapped to the Summary property. |

> *Note:* You should configure the **Display Status** of these properties. Hiding properties is recommended for "machine style data" used for checks or filtering that is not essential for component owners to see. Since the property values will be managed by the integration, they may be locked against manual UI modification.

## Step 2: Set up Custom Integration Mapping in OpsLevel

A Custom Integration provides a webhook endpoint to receive the JSON payload from Policy Reporter.

1.  Navigate to **Integrations** and select **Custom Integration**.
2.  Create the integration and obtain the **Webhook URL**. This is the endpoint that Policy Reporter will target.
3.  Configure the **Extraction Definition** (Stage 1) and **Transform Definition** (Stage 2).

### 2A. Extraction Definition

The extraction definition specifies how OpsLevel processes and stores the incoming Policy Reporter data.

```yaml
---
extractors:
- external_kind: kyverno_issues
  external_id: .resource.name + "-" + .rule
  exclude: (.rule | IN("check-for-application-label", "run-as-non-root-user", "run-as-non-root", "validate-readOnlyRootFilesystem", "check-pod-resources")) | not
  expires_after_days: 20
```
*   `external_kind: kyverno_issues` identifies the data type.
*   `external_id`: `.resource.name + "-" + .rule` creates a unique identifier for the issue object in the external system.
*   `exclude`: This JQ expression filters out results from specified Kyverno rules.
*   `expires_after_days`: If an issue component is not updated within 20 days, it is automatically deleted. This uses the **expiry feature**.

### 2B. Transform Definition

The transform definition maps the extracted data to the newly created `kyverno_issue` component type and its custom properties.

```yaml
---
transforms:
- external_kind: kyverno_issues
  on_component_not_found: create
  opslevel_kind: kyverno_issue
  opslevel_identifier: .resource.name + "-" + .rule
  properties:
    summary: ".message"
    status: ".status"
    namespace: ".resource.namespace"
    resource_name: ".resource.name"
    severity: ".severity"
    priority: ".priority"
    category: ".category"

- external_kind: kyverno_issues
  on_component_not_found: create
  opslevel_kind: namespace
  opslevel_identifier: ".resource.namespace"
```
*   The first block targets the `kyverno_issue` Component Type, using the unique combination of resource name and rule as the `opslevel_identifier`.
*   `on_component_not_found: create` ensures that if a violation is received for a new rule/resource combination, a new `Kyverno Issue` component is automatically created.
*   The `properties` section performs the essential mapping from the incoming data fields (using JQ expressions, e.g., `".message"`) to the defined OpsLevel Custom Properties (e.g., `summary`).
*   The second block is included from the sources to demonstrate linking the issue to the resource namespace component type.

## Step 3: Configure Kyverno Policy Reporter Webhook

The Policy Reporter must be configured to send its violation results to the OpsLevel webhook endpoint. This configuration is done in the Policy Reporter's configuration file (e.g., `values.yaml` if installed via Helm).

Locate the `webhook` section in the Policy Reporter configuration:

```yaml
webhook:
  host: "YOUR_OPSLEVEL_CUSTOM_INTEGRATION_WEBHOOK_URL"
  headers: {}
  minimumPriority: "" 
  skipExistingOnStartup: true
  sources: []
  filter:
    namespaces:
      include: []
      exclude: []
    policies:
      include: []
      exclude: []
    priorities:
      include: []
      exclude: []
    channels: []
```
1.  Set the **`host`** key to the **Webhook URL** obtained from your OpsLevel Custom Integration Mapping in Step 2.
2.  Apply the configuration changes to the Policy Reporter deployment.

Upon receiving the data, OpsLevel's custom integration will extract and transform the payload, creating or updating the `Kyverno Issue` components and populating them with the detailed violation data, automatically managed by the integration.