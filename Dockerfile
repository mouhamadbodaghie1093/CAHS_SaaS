# Use an official base image with required tools
FROM debian:latest

WORKDIR /workspace

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    openjdk-11-jre \
    && rm -rf /var/lib/apt/lists/*

# Install Nextflow
RUN curl -fsSL https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow

# Verify installation
RUN nextflow -version

ENTRYPOINT ["nextflow"]
