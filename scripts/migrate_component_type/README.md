# OpsLevel Bulk Service Component Type Updater

A Python command-line utility for bulk updating the Component Type of OpsLevel services. Services are filtered efficiently using multiple criteria directly supported by the OpsLevel GraphQL API.

---

## ⚠️ Requirements

* **Python 3.6+**
* **Dependencies:** `requests`, `argparse` (standard library), `sys`, `os` (standard library)
* **OpsLevel API Token:** A valid OpsLevel API Token with appropriate write permissions (Mutations).

---

## 💡 Prerequisites and Notes

Before running this script, it is crucial to understand the implications of changing a Service's Component Type, especially regarding Checks and Scorecards.

* **Read Official Documentation:** For full details on the impact of this change, please consult the official OpsLevel documentation on [Changing Component Types](https://docs.opslevel.com/docs/components#changing-types).
* **Type Exists:** Ensure the Component Type specified by your `--target-type-id` already exists in OpsLevel.
* **Check Compatibility:** When changing a Component Type, any **Service Checks** that were previously inherited from the *old* Component Type will be removed if they are not also part of the *new* Component Type. This may immediately change the Scorecard status of the affected services.
* **Scorecard Recalculation:** Scorecards will be immediately recalculated for all affected services after the update is complete.

---

## ⚙️ Usage

The script requires several mandatory arguments to define the filtering criteria and the target Component Type ID.

### Command Structure

```bash
python bulk_update_services.py \
    --target-type-id <NEW_TYPE_ID> \
    --source-type-id-filter <OLD_TYPE_ID> \
    --tag-arg <TAG_EQUALS> \
    --tag-arg-1 <TAG_DOES_NOT_EQUAL> \
    [--dry-run]