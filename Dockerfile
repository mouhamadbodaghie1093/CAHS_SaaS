# Use Debian Bookworm as base image
FROM debian:bookworm-slim

WORKDIR /workspace

# Fix missing package sources and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    bash \
    ca-certificates \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    openjdk-17-jre \
    && rm -rf /var/lib/apt/lists/*

# Check pip version and upgrade if necessary
RUN python3 -m pip install --upgrade pip

# Install Dash dependencies
RUN pip3 install dash dash-bootstrap-components flask

# Install Nextflow
RUN curl -fsSL https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow

# Verify Nextflow installation
RUN nextflow -version

# Copy your app and other necessary files into the container
COPY . /workspace

# Set the environment variable for Flask app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 8050 to be accessible from outside the container
EXPOSE 8050

# Define the command to start the Dash application
CMD ["python3", "app.py"]
