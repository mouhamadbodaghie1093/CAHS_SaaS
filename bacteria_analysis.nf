nextflow.enable.dsl=2

process BacteriaAnalysis {
    input:
    tuple val(sample_id), path(fastq_files)

    output:
    path("${sample_id}_bacteria_results.txt")

    script:
    """
    bacteria_tool --input ${fastq_files} --output ${sample_id}_bacteria_results.txt
    """
}

workflow {
    samples_ch = Channel.fromPath("data/*.fastq").map { file -> tuple(file.baseName, file) }
    BacteriaAnalysis(samples_ch)
}
