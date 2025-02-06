#!/bin/bash

# Install Java (required for Nextflow)
echo "Installing Java..."
apt-get update && apt-get install -y openjdk-11-jre-headless

# Verify Java installation
java -version

# Make sure Nextflow exists in the repository root
if [ -f "./nextflow" ]; then
    echo "Nextflow found in repository."
else
    echo "Nextflow not found in repository!"
    exit 1
fi

# Make Nextflow executable
chmod +x nextflow

# Move Nextflow to a system path
mv nextflow /usr/local/bin/

# Verify installation
which nextflow
ls -l /usr/local/bin/nextflow
nextflow -version
