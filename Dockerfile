FROM nextflow/nextflow

WORKDIR /workspace
COPY . /workspace

CMD ["nextflow", "run", "main.nf"]
