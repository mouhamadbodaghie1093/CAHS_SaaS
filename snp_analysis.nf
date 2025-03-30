process SNPAnalysis {
    input:
    tuple val(sample_id), path(fastq_files)

    output:
    path("results/${sample_id}_snp_results.vcf")

    script:
    """
    snp_tool --input ${fastq_files} --output results/${sample_id}_snp_results.vcf
    """
}

workflow SNPWorkflow {
    samples_ch = Channel.fromPath("data/*.fastq").map { file -> tuple(file.baseName.replace('.fastq', ''), file) }
    SNPAnalysis(samples_ch)
}
