#!/bin/bash

set -e  # Exit on error

echo "Checking if Java is available..."
if ! command -v java &> /dev/null; then
    echo "Java is not found! Installing a prebuilt version..."
    export JAVA_HOME="/opt/render/project/.render/java11"
    export PATH="$JAVA_HOME/bin:$PATH"
fi

# Verify Java installation
java -version

# Ensure Python dependencies are installed
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install gunicorn dash dash-bootstrap-components

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn -w 4 --bind 0.0.0.0:8080 app:server
