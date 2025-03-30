# Use Debian Bookworm as base image
FROM debian:bookworm-slim

WORKDIR /workspace

# Install dependencies and clean up to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Create and activate virtual environment, install pip dependencies
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

# Install Nextflow
RUN curl -fsSL https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow && \
    nextflow -version

# Ensure Python is accessible as 'python'
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set Nextflow home to a writable directory inside /workspace
ENV NXF_HOME=/workspace/.nextflow

# Create .nextflow directory with proper permissions
RUN mkdir -p /workspace/.nextflow && chmod 775 /workspace/.nextflow

# Copy application files into the container
COPY . /workspace

# Set environment variables for Flask app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose necessary port
EXPOSE 8050

# Define the command to start the Dash application
CMD ["/opt/venv/bin/python3", "app.py"]
