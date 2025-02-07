#!/bin/bash

set -e  # Exit on error

# Define JAVA_HOME in a writable directory
export JAVA_HOME="$HOME/java"
export PATH="$JAVA_HOME/bin:$HOME/.local/bin:$PATH"

# Download and install Java in the writable directory
echo "Downloading and installing Java..."
curl -o openjdk.tar.gz https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz
mkdir -p "$JAVA_HOME"
tar -xzf openjdk.tar.gz -C "$JAVA_HOME" --strip-components=1

# Verify Java installation
java -version

# Install Nextflow
echo "Installing Nextflow..."
curl -s https://get.nextflow.io | bash
chmod +x nextflow

# Ensure $HOME/.local/bin exists
mkdir -p "$HOME/.local/bin"

# Move Nextflow to a directory in PATH
mv nextflow "$HOME/.local/bin/"

# Double-check Nextflow installation
if [ -f "$HOME/.local/bin/nextflow" ]; then
    echo "Nextflow installed successfully!"
else
    echo "Nextflow installation failed!"
    exit 1
fi

# Verify Nextflow
export PATH="$HOME/.local/bin:$PATH"
nextflow -version

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install gunicorn dash dash-bootstrap-components

# Start Gunicorn
#echo "Starting Gunicorn..."
#gunicorn -w 4 --bind 0.0.0.0:8080 app:server
