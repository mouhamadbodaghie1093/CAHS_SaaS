#!/bin/bash

set -e  # Exit on error

# Ensure SDKMAN is installed
if [ ! -d "$HOME/.sdkman" ]; then
    echo "Installing SDKMAN..."
    curl -s "https://get.sdkman.io" | bash
    source "$HOME/.sdkman/bin/sdkman-init.sh"
else
    source "$HOME/.sdkman/bin/sdkman-init.sh"
fi

echo "Installing Java using SDKMAN..."
sdk install java 11.0.20-tem

# Verify Java installation
java -version

# Check if Nextflow exists and download if not
echo "Checking if Nextflow exists..."
if [ ! -f "./nextflow" ]; then
    echo "Nextflow not found in repository! Downloading..."
    curl -v https://get.nextflow.io -o nextflow
    if [ $? -ne 0 ]; then
        echo "Failed to download Nextflow."
        exit 1
    fi
fi

echo "Making Nextflow executable..."
chmod +x nextflow
ls -l nextflow  # Ensure permissions are correct

echo "Running Nextflow..."
./nextflow -version 2> nextflow_error.log
echo "Nextflow error log saved to nextflow_error.log"

# Ensure Python is installed
echo "Checking if Python is installed..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found! Please install Python3."
    exit 1
fi

# Ensure pip is installed and upgrade
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install gunicorn dash dash-bootstrap-components

# List installed Python packages
pip3 list

echo "Starting Gunicorn on port 8080..."

# Running Gunicorn without --reload (this avoids the restart loop issue in production)
gunicorn -w 4 --bind 0.0.0.0:8080 app:server

# If you want to continue with a development environment that needs automatic reloading,
# you can uncomment the following line to use the --reload flag:
# gunicorn --reload -w 4 --bind 0.0.0.0:8080 app:server
