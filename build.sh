#!/bin/bash

set -e  # Exit on error

# Install Java manually
echo "Downloading and installing Java..."
curl -o openjdk.tar.gz https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz
mkdir -p /opt/java
tar -xzf openjdk.tar.gz -C /opt/java --strip-components=1
export JAVA_HOME="/opt/java"
export PATH="$JAVA_HOME/bin:$PATH"

# Verify Java installation
java -version

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install gunicorn dash dash-bootstrap-components

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn -w 4 --bind 0.0.0.0:8080 app:server
