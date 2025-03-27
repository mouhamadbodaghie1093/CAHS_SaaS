#!/usr/bin/env nextflow

params.input = file(params.input ?: 'input.fastq')
params.bam = file(params.bam ?: 'input.bam')

process SNP_Analysis {
    input:
    path fastq_file from params.input
    path bam_file from params.bam

    output:
    path "snp_results.vcf"

    script:
    """
    echo "Running SNP analysis on FASTQ: $fastq_file and BAM: $bam_file"
    bcftools mpileup -Ou -f reference.fasta $bam_file | bcftools call -mv -Oz -o snp_results.vcf.gz
    bcftools index snp_results.vcf.gz
    """
}
