#!/bin/bash

# Function to show usage instructions
usage() {
    echo "Usage: $0 {-i|-d} <package-name> [pip-options]"
    echo "  -i: Install a package and update requirements.txt"
    echo "  -d: Uninstall a package and update requirements.txt"
    exit 1
}

# If no arguments are provided, install all dependencies from requirements.txt
if [ "$#" -eq 0 ]; then
    echo "No arguments provided. Installing all dependencies from requirements.txt..."
    pip install -r requirements.txt
    # Update requirements.txt after installation
    # pip freeze > requirements.txt
    echo "requirements.txt updated."
    exit 0
fi

# Check if sufficient arguments are provided for other operations
if [ "$#" -lt 2 ]; then
    usage
fi

# Extract operation and package name
operation=$1
package=$2

# Shift the arguments to allow passing optional pip options like -U
shift 2
pip_options="$@"

# Perform the requested operation
case $operation in
    -i)
        echo "Installing $package with options: $pip_options..."
        pip install "$package" $pip_options
        ;;
    -d)
        echo "Uninstalling $package..."
        pip uninstall -y "$package"
        ;;
    *)
        echo "Invalid operation: $operation"
        usage
        ;;
esac

# Update requirements.txt after the operation
pip freeze > requirements.txt

echo "Operation '$operation' on '$package' completed. requirements.txt updated."

