#!/bin/bash
#!/bin/bash

set -e  # Exit on error

# Ensure Java is available
echo "Checking if Java is installed..."
if ! command -v java &> /dev/null; then
    echo "Java is not available. Ensure JAVA_VERSION is set in Render."
    exit 1
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

set -e  # Exit on error

# Ensure Java is available
echo "Checking if Java is installed..."
if ! command -v java &> /dev/null; then
    echo "Java is not available. Ensure JAVA_VERSION is set in Render."
    exit 1
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
