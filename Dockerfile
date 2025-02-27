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

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip

# Install necessary Python dependencies inside the virtual environment
RUN /opt/venv/bin/pip install \
    dash==2.9.3 \
    dash-bootstrap-components==1.0.3 \
    dash-core-components==2.0.0 \
    dash-html-components==2.0.0 \
    dash-table==5.0.0 \
    Flask==2.2.2 \
    Werkzeug==2.2.3 \
    pandas==1.5.3 \
    plotly==5.9.0 \
    numpy==1.24.1 \
    requests==2.28.2 \
    gunicorn==21.2.0 \
    biopython

# Install matplotlib for plotting (if needed)
RUN /opt/venv/bin/pip install matplotlib

# Install Nextflow
RUN curl -fsSL https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow

# Verify Nextflow installation
RUN nextflow -version

# Set NXF_HOME to a writable directory inside /workspace
ENV NXF_HOME=/workspace/.nextflow

# Create .nextflow directory with proper permissions
RUN mkdir -p /workspace/.nextflow && \
    chmod 777 /workspace/.nextflow

# Copy your app and other necessary files into the container
COPY . /workspace

# Set the environment variable for Flask app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 8050 to be accessible from outside the container
EXPOSE 8050

# Define the command to start the Dash application
CMD ["/opt/venv/bin/python3", "app.py"]
