#!/bin/bash

show_menu() {
    echo "Select an option:"
    echo "1) List out all infrastructure resources by name and id"
    echo "2) Delete all infrastructure resources"
    echo "3) Exit"
}

run_command_1() {
    echo "Listing out all infrastructure resources by name and id"

    infra_resources=$(opslevel list infra -o json)
    infra_resources_count=$(echo $infra_resources | jq '.[] | .id' | wc -l)
    echo $infra_resources | jq '.[] | [.id, .name] | @csv'
    echo "Infrastructure resources COUNT: $infra_resources_count"
}

run_command_2() {
    num_infra_resources=$(opslevel list infra -o json | jq '.[] | .id' | wc -l)
    echo "Number of infrastructure resources to be deleted: $num_infra_resources"
    read -p "Are you sure you want to delete all infrastructure resources? (y/n) " confirm

    if [[ $confirm == "y" ]]; then
        opslevel list infra -o json | jq '.[] | .id' | xargs -P 10 -n1 opslevel delete infra
    else
        echo "y not entered. Aborting..."
    fi
}

# Main script logic
while true; do
    show_menu
    read -p "Enter your choice: " choice
    case $choice in
        1)
            run_command_1
            ;;
        2)
            run_command_2
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please select 1, 2, or 3."
            ;;
    esac
done