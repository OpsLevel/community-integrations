#!/bin/bash

show_menu() {
    echo "Select an option:"
    echo "1) List out all services by name and id"
    echo "2) Delete all services"
    echo "3) Exit"
}

run_command_1() {
    echo "Listing out all services by name and id"

    services=$(opslevel list services -o json)
    services_count=$(echo $services | jq '.[] | .id' | wc -l)
    echo $services | jq '.[] | [.id, .name] | @csv'
    echo "Infrastructure resources COUNT: $services_count"
}

run_command_2() {
    services_count=$(opslevel list services -o json | jq '.[] | .id' | wc -l)
    echo "Number of services to be deleted: $services_count"
    read -p "Are you sure you want to delete all services? (y/n) " confirm

    if [[ $confirm == "y" ]]; then
        opslevel list services -o json | jq '.[] | .id' | xargs -P 10 -n1 opslevel delete service
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