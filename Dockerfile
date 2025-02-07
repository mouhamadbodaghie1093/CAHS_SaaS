FROM nfcore/base:latest

WORKDIR /workspace

# Install Nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/

ENTRYPOINT ["nextflow"]
