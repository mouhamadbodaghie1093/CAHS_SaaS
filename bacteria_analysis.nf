nextflow.enable.dsl=2

params.input = "/home/mouhamadbodaghie/PycharmProjects/CAHS_SaaS/input_data/input_dada.fastq"
params.output = "analysis_results.html"  // Default output file

process bacteria_analysis {
    input:
    path input_file

    output:
    path "analysis_results.html"

    script:
    """
    python /correct/path/to/bacteria_analysis.py --input ${input_file} --output analysis_results.html --no-server
    """
}
workflow {
    // Convert input file path to Nextflow channel
    input_channel = Channel.fromPath(params.input)

    // Run bacteria analysis with input channel
    bacteria_analysis(input_channel)
}
