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
    curl -s https://get.nextflow.io -o nextflow
    if [ $? -ne 0 ]; then
        echo "Failed to download Nextflow."
        exit 1
    fi
fi

echo "Making Nextflow executable..."
chmod +x nextflow

echo "Running Nextflow..."
./nextflow -version

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

echo "Starting Gunicorn..."
gunicorn -w 4 app:server
