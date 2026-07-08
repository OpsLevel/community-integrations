import argparse
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
                totalCount
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
                totalCount
                filteredCount
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


# Function to make a GraphQL query
def opslevel_graphql_query(query, variables=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPSLEVEL_API_TOKEN}",
    }
    data = {"query": query, "variables": variables}
    response = requests.post(OPSLEVEL_ENDPOINT, json=data, headers=headers)
    return response.json()


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


def export_opslevel_yml_files(selected_aliases, excluded_sections, dry_run=False):
    end_cursor = None
    has_next_page = True
    skipped_count = 0
    exported_count = 0

    with open(SKIPPED_COMPONENTS_FILE, "w") as skipped_file:
        while has_next_page:
            response = opslevel_graphql_query(
                LIST_SERVICES_QUERY, variables={"endCursor": end_cursor}
            )
            nodes = response["data"]["account"]["services"]["nodes"]
            for node in nodes:
                component_type = node["type"]["alias"]
                if component_type not in selected_aliases:
                    continue

                if not has_linked_repo(node):
                    skipped_file.write(f"{node['htmlUrl']}\n")
                    skipped_count += 1
                    continue

                service_slug = node["slug"]
                if dry_run:
                    exported_count += 1
                    print(
                        f"[dry-run] Would export: "
                        f"{component_type}/{service_slug}/opslevel.yml"
                    )
                    continue

                service_id = node["id"]
                response_2 = opslevel_graphql_query(
                    FETCH_OPSLEVEL_YML_FOR_SERVICE_QUERY, variables={"id": service_id}
                )
                yaml_data = response_2["data"]["account"]["configFile"]["yaml"]
                yaml_data = post_process_opslevel_yml(yaml_data, excluded_sections)
                output_dir = os.path.join(OUTPUT_BASE_DIR, component_type, service_slug)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "opslevel.yml")
                with open(output_path, "w") as f:
                    f.write(yaml_data)
                exported_count += 1

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

    if skipped_count:
        print(
            f"Skipped {skipped_count} component(s) with no linked repo. "
            f"See {SKIPPED_COMPONENTS_FILE}."
        )


def post_process_opslevel_yml(yaml_data, excluded_sections):
    if "properties" not in excluded_sections:
        return yaml_data

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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export OpsLevel opslevel.yml files for all components."
    )
    parser.add_argument(
        "--include",
        nargs="+",
        choices=["properties"],
        default=[],
        metavar="SECTION",
        help="Include optional YAML sections in the export (default: properties are excluded)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "List components that would be exported without writing opslevel.yml files. "
            "Still writes skipped_components_with_missing_repo_links.txt."
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

    selected_aliases = prompt_component_type_selection(component_types)
    if args.dry_run:
        print("\n[dry-run] No opslevel.yml files will be written.")
    print(f"\nExporting opslevel.yml for: {', '.join(sorted(selected_aliases))}")
    export_opslevel_yml_files(selected_aliases, excluded_sections, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
