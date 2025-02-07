FROM nfcore/base:latest

WORKDIR /workspace

# Install dependencies
RUN apt-get update && apt-get install -y curl bash

# Install Nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow

ENTRYPOINT ["nextflow"]