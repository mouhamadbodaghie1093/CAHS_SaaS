# Use Debian Bookworm as base image
FROM debian:bookworm-slim

# Set working directory
WORKDIR /workspace

# Fix missing package sources and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    bash \
    ca-certificates \
    openjdk-17-jre \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable (important for Java applications)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Nextflow
RUN curl -fsSL https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow && \
    chown root:root /usr/local/bin/nextflow

# Verify installation
RUN nextflow -version

# Optionally: Create a non-root user and switch to it (if desired)
# RUN useradd -ms /bin/bash nextflowuser
# USER nextflowuser

# Default entrypoint to execute Nextflow
ENTRYPOINT ["nextflow"]
