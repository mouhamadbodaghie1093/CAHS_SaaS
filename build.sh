#!/bin/bash

# Set up a local bin directory in the home directory
mkdir -p $HOME/bin
export PATH=$PATH:$HOME/bin

# Install Java in a user-writable directory
echo "Downloading and installing Java..."
curl -o jre.tar.gz https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
mkdir -p $HOME/java
tar -xzf jre.tar.gz -C $HOME/java --strip-components=1
export JAVA_HOME=$HOME/java
export PATH=$PATH:$JAVA_HOME/bin

# Verify Java installation
java -version || { echo "Java installation failed!"; exit 1; }

# Ensure Nextflow is executable and in the repository
if [ -f "./nextflow" ]; then
    echo "Nextflow found in repository."
else
    echo "Nextflow not found in repository!"
    exit 1
fi

# Move Nextflow to $HOME/bin
chmod +x nextflow
mv nextflow $HOME/bin/ || { echo "Failed to move Nextflow!"; exit 1; }

# Verify Nextflow installation
which nextflow
ls -l $HOME/bin/nextflow
nextflow -version || { echo "Nextflow command failed!"; exit 1; }

# Install Python dependencies (if needed)
pip install -r requirements.txt
