import argparse
import contextlib
import os
import sys

import requests

OPSLEVEL_API_TOKEN = os.environ["OPSLEVEL_API_TOKEN"]
OPSLEVEL_ENDPOINT = "https://app.opslevel.com/graphql"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_BASE_DIR = os.path.join(SCRIPT_DIR, "opslevelyml_repo")
SKIPPED_COMPONENTS_FILE = os.path.join(
    SCRIPT_DIR, "skipped_components_with_missing_repo_links.txt"
)
DEFAULT_EXCLUDED_SECTIONS = {"properties"}

COMPONENT_TYPES_QUERY = """
    query componentTypes($endCursor: String) {
        account {
            componentTypes(after: $endCursor) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    alias
                    category
                }
            }
        }
    }
"""

LIST_SERVICES_QUERY = """
    query services($endCursor: String) {
        account {
            services(componentCategory: "default", after: $endCursor) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    name
                    slug
                    type {
                        id
                        alias
                    }
                    htmlUrl
                    repos {
                        nodes {
                            id
                        }
                    }
                }
            }
        }
    }
"""

FETCH_OPSLEVEL_YML_FOR_SERVICE_QUERY = """
    query get_opslevel_yml($id: ID!) {
        account {
            configFile(id: $id) {
                ownerType
                yaml
            }
        }
    }
"""


def opslevel_graphql_query(query, variables=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPSLEVEL_API_TOKEN}",
    }
    data = {"query": query, "variables": variables}
    response = requests.post(OPSLEVEL_ENDPOINT, json=data, headers=headers)

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"OpsLevel API request failed with HTTP {response.status_code}: "
            f"{response.text}"
        ) from exc

    payload = response.json()
    if errors := payload.get("errors"):
        messages = "; ".join(
            error.get("message", str(error)) for error in errors
        )
        raise RuntimeError(f"OpsLevel GraphQL error: {messages}")

    if not payload.get("data"):
        raise RuntimeError(f"OpsLevel API returned no data: {payload}")

    return payload


def fetch_default_component_types():
    end_cursor = None
    has_next_page = True
    component_types = []

    while has_next_page:
        response = opslevel_graphql_query(
            COMPONENT_TYPES_QUERY, variables={"endCursor": end_cursor}
        )
        nodes = response["data"]["account"]["componentTypes"]["nodes"]
        component_types.extend(
            component_type
            for component_type in nodes
            if component_type["category"] == "default"
        )
        page_info = response["data"]["account"]["componentTypes"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]

    return component_types


def prompt_component_type_selection(component_types):
    print(
        "\nSelect component type(s) to export opslevel.yml for "
        "(comma-separated numbers, or enter 'a' for all):"
    )
    for index, component_type in enumerate(component_types, start=1):
        print(f"{index}. {component_type['alias']}")

    while True:
        selection = input("> ").strip().lower()
        if selection == "a":
            return {component_type["alias"] for component_type in component_types}

        try:
            selected_indexes = [
                int(value.strip()) for value in selection.split(",") if value.strip()
            ]
        except ValueError:
            print("Invalid input. Enter comma-separated numbers or 'a' for all.")
            continue

        if not selected_indexes:
            print("No component types selected. Try again.")
            continue

        if any(index < 1 or index > len(component_types) for index in selected_indexes):
            print(f"Enter numbers between 1 and {len(component_types)}, or 'a' for all.")
            continue

        return {
            component_types[index - 1]["alias"]
            for index in selected_indexes
        }


def has_linked_repo(node):
    repos = node.get("repos") or {}
    repo_nodes = repos.get("nodes") or []
    return any(repo.get("id") for repo in repo_nodes)


def get_component_type_alias(node):
    component_type = node.get("type") or {}
    return component_type.get("alias")


def write_opslevel_yml_for_component(node, component_type, excluded_sections):
    service_slug = node["slug"]
    service_id = node["id"]
    response = opslevel_graphql_query(
        FETCH_OPSLEVEL_YML_FOR_SERVICE_QUERY, variables={"id": service_id}
    )
    yaml_data = response["data"]["account"]["configFile"]["yaml"]
    yaml_data = post_process_opslevel_yml(yaml_data, excluded_sections)
    output_dir = os.path.join(OUTPUT_BASE_DIR, component_type, service_slug)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "opslevel.yml")
    with open(output_path, "w") as f:
        f.write(yaml_data)


def export_opslevel_yml_files(
    selected_aliases, excluded_sections, dry_run=False, include_no_repo=False
):
    end_cursor = None
    has_next_page = True
    skipped_count = 0
    skipped_no_type_count = 0
    no_repo_exported_count = 0
    exported_count = 0

    with contextlib.ExitStack() as stack:
        skipped_file = None
        if not include_no_repo:
            skipped_file = stack.enter_context(open(SKIPPED_COMPONENTS_FILE, "w"))

        while has_next_page:
            response = opslevel_graphql_query(
                LIST_SERVICES_QUERY, variables={"endCursor": end_cursor}
            )
            nodes = response["data"]["account"]["services"]["nodes"]
            for node in nodes:
                component_type = get_component_type_alias(node)
                if not component_type:
                    skipped_no_type_count += 1
                    continue

                if component_type not in selected_aliases:
                    continue

                missing_repo = not has_linked_repo(node)
                if missing_repo and skipped_file is not None:
                    skipped_file.write(f"{node['htmlUrl']}\n")
                    skipped_count += 1
                    continue

                service_slug = node["slug"]
                if dry_run:
                    exported_count += 1
                    if missing_repo:
                        no_repo_exported_count += 1
                    print(
                        f"[dry-run] Would export: "
                        f"{component_type}/{service_slug}/opslevel.yml"
                    )
                    continue

                write_opslevel_yml_for_component(node, component_type, excluded_sections)
                exported_count += 1
                if missing_repo:
                    no_repo_exported_count += 1

            page_info = response["data"]["account"]["services"]["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            end_cursor = page_info["endCursor"]

    if dry_run:
        print(
            f"\n[dry-run] Would export {exported_count} component(s). "
            f"No files written to {OUTPUT_BASE_DIR}."
        )
    else:
        print(f"\nExported {exported_count} component(s) to {OUTPUT_BASE_DIR}.")

    if include_no_repo:
        if no_repo_exported_count:
            print(
                f"Included {no_repo_exported_count} component(s) with no linked repo."
            )
    else:
        print(
            f"Skipped {skipped_count} component(s) with no linked repo. "
            f"See {SKIPPED_COMPONENTS_FILE}."
        )

    if skipped_no_type_count:
        print(
            f"Skipped {skipped_no_type_count} component(s) with no component type."
        )


def post_process_opslevel_yml(yaml_data, excluded_sections):
    if "properties" not in excluded_sections:
        return yaml_data

    # Strip excluded sections line-by-line instead of parsing with a YAML library
    # so OpsLevel's original formatting, key order, and comments are preserved.
    # This assumes OpsLevel emits top-level keys with 2-space indentation.
    lines = yaml_data.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip("\n\r")
        if stripped == "  properties:":
            key_indent = 2
            i += 1
            while i < len(lines):
                sibling = lines[i].rstrip("\n\r")
                if sibling and (len(sibling) - len(sibling.lstrip(" "))) <= key_indent:
                    break
                i += 1
            continue

        result.append(line)
        i += 1

    return "".join(result)


def resolve_component_type_selection(component_types, component_type_args):
    available_aliases = {component_type["alias"] for component_type in component_types}

    if component_type_args is None:
        return prompt_component_type_selection(component_types)

    selected_aliases = set(component_type_args)
    unknown_aliases = sorted(selected_aliases - available_aliases)
    if unknown_aliases:
        print(
            "Unknown component type(s): "
            f"{', '.join(unknown_aliases)}. "
            f"Available: {', '.join(sorted(available_aliases))}",
            file=sys.stderr,
        )
        sys.exit(1)

    return selected_aliases


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export OpsLevel opslevel.yml files for all components."
    )
    parser.add_argument(
        "--component-types",
        nargs="+",
        metavar="ALIAS",
        help=(
            "Component type aliases to export (e.g. service backend). "
            "Skips the interactive prompt."
        ),
    )
    parser.add_argument(
        "--include",
        nargs="+",
        choices=sorted(DEFAULT_EXCLUDED_SECTIONS),
        default=[],
        metavar="SECTION",
        help="Include optional YAML sections in the export (default: properties are excluded)",
    )
    parser.add_argument(
        "--include-no-repo",
        action="store_true",
        help=(
            "Also export components with no linked repository. "
            "By default these are skipped and written to "
            "skipped_components_with_missing_repo_links.txt."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "List components that would be exported without writing opslevel.yml files. "
            "Still writes skipped_components_with_missing_repo_links.txt unless "
            "--include-no-repo is set."
        ),
    )
    return parser.parse_args()


# Main function to execute the script
def main():
    args = parse_args()
    excluded_sections = DEFAULT_EXCLUDED_SECTIONS - set(args.include)

    component_types = fetch_default_component_types()
    if not component_types:
        print("No component types with category 'default' were found.", file=sys.stderr)
        sys.exit(1)

    selected_aliases = resolve_component_type_selection(
        component_types, args.component_types
    )
    if args.dry_run:
        print("\n[dry-run] No opslevel.yml files will be written.")
    print(f"\nExporting opslevel.yml for: {', '.join(sorted(selected_aliases))}")
    export_opslevel_yml_files(
        selected_aliases,
        excluded_sections,
        dry_run=args.dry_run,
        include_no_repo=args.include_no_repo,
    )


if __name__ == "__main__":
    main()
