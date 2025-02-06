#!/bin/bash

set -e  # Exit on error

echo "Installing Java using SDKMAN..."
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Install Java 11 (LTS version compatible with Nextflow)
sdk install java 11.0.20-tem

# Verify Java installation
java -version

echo "Checking if Nextflow exists..."
if [ ! -f "./nextflow" ]; then
    echo "Nextflow not found in repository! Downloading..."
    curl -s https://get.nextflow.io -o nextflow
fi

echo "Making Nextflow executable..."
chmod +x nextflow

echo "Running Nextflow..."
./nextflow -version
