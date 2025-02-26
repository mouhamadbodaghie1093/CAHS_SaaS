nextflow.enable.dsl = 2

params.input = ""
params.output = "results"

process analyze_bacteria {
tag "$params.input"
publishDir params.output, mode: 'copy'

input:
path input_file from file(params.input)  // Correcting how input is passed

    output:
path "analysis_results.html"

    script:
def extension = input_file.name.tokenize('.')
def is_gzipped = extension[-1]== 'gz'
def file_type = is_gzipped ? extension[-2]: extension[-1]

if (file_type in ['fastq', 'fasta']) {
"""
python analyze_bacteria.py --input $input_file --output analysis_results.html
"""
} else {
error "Unsupported file format: $input_file"
}
}

workflow {
if (!params.input) {
error "No input file specified.Use '--input < file>' when running Nextflow."
    }

    analyze_bacteria()
}
