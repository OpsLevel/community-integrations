# Set GitHub custom properties from the repository (optional)

GitHub doesn't read custom properties from files in a repository: they're set in the UI or through the API. These
three files let each repository keep its `data_classification` and `external_interface_type` in code, reviewed like
any other change, and push them to GitHub on merge. OpsLevel picks the new values up on its next sync and
recomputes the repository's Risk Priority.

| File (copy into each repository) | What it does |
|---|---|
| [`.github/repo-properties.yml`](.github/repo-properties.yml) | The two values and a one-line reason |
| [`.github/workflows/sync-repo-properties.yml`](.github/workflows/sync-repo-properties.yml) | On a push to `main` that changes the file (or a manual run), sets the values with `PATCH /repos/{owner}/{repo}/properties/values` |
| [`.github/CODEOWNERS`](.github/CODEOWNERS) | Requires your security team's review for changes to the file and workflow. Merge these lines into an existing CODEOWNERS |

## Setup

1. In **GitHub → Organization settings → Custom properties**, define `data_classification` and
   `external_interface_type` and turn on **Allow repository actors to set this property** for both.
2. Create a GitHub App or fine-grained token with the repository permission **Custom properties: Read and write**
   on the org's repositories, and store it as the org secret `REPO_PROPERTIES_TOKEN`.
3. Copy the three files into each repository, set the values and the reason, and replace `@your-org/security`.
4. Turn on branch protection with **Require review from Code Owners** on `main`, so the CODEOWNERS rule is enforced.

The workflow uses `yq` and `gh`, both preinstalled on GitHub-hosted Ubuntu runners.

## Notes

- Whether the workflow's built-in `GITHUB_TOKEN` can set custom properties instead of a separate token hasn't been
  verified; the workflow doesn't rely on it.
- The token from the main guide (Metadata: Read) is only for OpsLevel's reads; it can't write custom properties.
