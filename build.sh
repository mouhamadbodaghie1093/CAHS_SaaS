#!/bin/bash

# Install OpenJDK (Java)
echo "Installing Java..."
apt-get update && apt-get install -y openjdk-11-jre-headless

# Verify Java installation
java -version

# Install Nextflow
echo "Downloading Nextflow..."
curl -s https://get.nextflow.io | bash

# Check if the Nextflow binary exists
if [ -f "./nextflow" ]; then
    echo "Nextflow installed successfully."
else
    echo "Nextflow installation failed!"
    exit 1
fi

# Move Nextflow to /usr/local/bin so it's globally accessible
mv nextflow /usr/local/bin/

# Verify that Nextflow is available in the path
which nextflow
ls -l /usr/local/bin/nextflow

# Install any Python dependencies (if applicable)
pip install -r requirements.txt
