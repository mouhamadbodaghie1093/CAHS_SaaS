#!/bin/bash

set -e  # Exit on error

echo "Installing system dependencies..."
apt-get update && apt-get install -y curl unzip

# Install Java (Avoid SDKMAN)
echo "Installing Java..."
apt-get install -y openjdk-11-jdk
java -version

# Check and Install Nextflow
echo "Checking if Nextflow exists..."
if [ ! -f "./nextflow" ]; then
    echo "Nextflow not found in repository! Downloading..."
    curl -s https://get.nextflow.io -o nextflow
    chmod +x nextflow
fi
./nextflow -version  # Validate installation

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install gunicorn dash dash-bootstrap-components

# List installed packages
pip3 list

echo "Starting Gunicorn..."
gunicorn -w 4 --bind 0.0.0.0:8080 app:server &  # Run in the background

echo "Build script completed."
