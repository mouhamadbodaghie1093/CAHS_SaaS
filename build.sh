#!/bin/bash

# Install OpenJDK (Java)
apt-get update && apt-get install -y openjdk-11-jre-headless

# Install Nextflow
curl -s https://get.nextflow.io | bash
mv nextflow /usr/local/bin/

# Install dependencies from requirements.txt (if applicable)
pip install -r requirements.txt
