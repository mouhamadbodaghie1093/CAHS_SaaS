FROM nfcore/base:latest

WORKDIR /workspace

# Install dependencies
RUN apt-get update && apt-get install -y curl

# Install Nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/

ENTRYPOINT ["nextflow"]
