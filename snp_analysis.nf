nextflow.enable.dsl=2

params.bam = null
params.reference = null
params.outdir = './results'

process snp_calling {

    input:
    path bam
    path reference

    output:
    path "snp_analysis_results.vcf"
    path "log.txt"

    script:
    """
    echo "Checking reference index..."
    if [ ! -f "${reference}.fai" ]; then
        echo "Indexing reference..."
        samtools faidx ${reference}
    else
        echo "Reference already indexed."
    fi

    echo "Running bcftools mpileup and call..."
    bcftools mpileup -f ${reference} ${bam} | bcftools call -mv -Ov -o snp_analysis_results.vcf

    echo "Process complete." > log.txt
    """
}

workflow {

    // Validate input parameters
    if (!params.bam) {
        error "Missing required parameter: --bam"
    }
    if (!params.reference) {
        error "Missing required parameter: --reference"
    }

    // Check if input files exist before starting
    if (!file(params.bam).exists()) {
        error "BAM file does not exist: ${params.bam}"
    }
    if (!file(params.reference).exists()) {
        error "Reference FASTA file does not exist: ${params.reference}"
    }

    // Create output directory if not exists
    def outDir = file(params.outdir)
    if (!outDir.exists()) {
        outDir.mkdirs()
    }

    // Create channels from input paths
    bam_ch = Channel.fromPath(params.bam)
    reference_ch = Channel.fromPath(params.reference)

    // Run the process and capture outputs
    def results = snp_calling(bam_ch, reference_ch)

    // Move outputs to outdir after completion
    results.snp_analysis_results_vcf.view()  // for debugging (optional)
    results.log_txt.view()                   // for debugging (optional)

    results.snp_analysis_results_vcf.into { vcf_files }
    results.log_txt.into { log_files }

    vcf_files.subscribe { file ->
        file.moveTo(outDir.resolve(file.name))
    }

    log_files.subscribe { file ->
        file.moveTo(outDir.resolve(file.name))
    }
}
