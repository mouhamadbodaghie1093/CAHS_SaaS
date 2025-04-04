nextflow.enable.dsl=2

params.fna = '/home/mouhamadbodaghie/PycharmProjects/CAHS_SaaS/uploaded_fna.fna'
params.bam = '/home/mouhamadbodaghie/PycharmProjects/CAHS_SaaS/uploaded_bam.bam'
params.reference = '/home/mouhamadbodaghie/PycharmProjects/CAHS_SaaS/test/ref.fna'

process snp_calling {
    input:
    path fna
    path bam
    path reference

    output:
    path 'results/snp_analysis_results.vcf'

    script:
    """
    # Create the results directory if it doesn't exist
    mkdir -p ./results

    # Ensure the reference genome is indexed
    if [ ! -f ${reference}.fai ]; then
        samtools faidx ${reference}
    fi

    # Perform variant calling using bcftools
    bcftools mpileup -f ${reference} ${bam} | bcftools call -mv -Ov -o ./results/snp_analysis_results.vcf
    """
}

workflow {
    // Create separate channels for each input parameter
    fna_ch = Channel.fromPath(params.fna)
    bam_ch = Channel.fromPath(params.bam)
    reference_ch = Channel.fromPath(params.reference)

    // Pass the channels as inputs to the snp_calling process
    snp_calling(fna_ch, bam_ch, reference_ch)

    // Collect the output of the snp_calling process
    snp_calling.out.subscribe { file ->
        println "VCF Output: $file"
    }
}
