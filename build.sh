#!/bin/bash

set -e  # Exit on error

echo "Checking if Nextflow exists..."
if [ ! -f "./nextflow" ]; then
    echo "Nextflow not found in repository! Downloading..."
    curl -s https://get.nextflow.io -o nextflow
fi

echo "Making Nextflow executable..."
chmod +x nextflow

echo "Checking Java installation..."
java -version || echo "Java not found! Consider using a container-based approach."

echo "Running Nextflow..."
./nextflow -version
