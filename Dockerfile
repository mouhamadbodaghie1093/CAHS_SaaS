# Use a stable Debian-based image
FROM debian:bookworm-slim

WORKDIR /workspace

# Fix missing package sources & install dependencies
RUN apt-get clean && apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    curl \
    bash \
    ca-certificates \
    openjdk-11-jre \
    && rm -rf /var/lib/apt/lists/*

# Install Nextflow
RUN curl -fsSL https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow

# Verify installation
RUN nextflow -version

ENTRYPOINT ["nextflow"]
