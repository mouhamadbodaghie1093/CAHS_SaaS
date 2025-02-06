#!/bin/bash

set -e  # Exit on error

# Ensure Java is installed (Render provides it)
echo "Using Java version:"
java -version

# Install Nextflow only if not present
echo "Checking if Nextflow exists..."
if [ ! -f "./nextflow" ]; then
    echo "Downloading Nextflow..."
    curl -s https://get.nextflow.io -o nextflow
    chmod +x nextflow
fi
./nextflow -version  # Validate installation

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install --no-cache-dir gunicorn dash dash-bootstrap-components

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn -w 4 --bind 0.0.0.0:8080 app:server &  # Run in background

echo "Build script completed successfully."
