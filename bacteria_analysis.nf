process TEST_RUN {
    script:
    """
    echo 'Nextflow is running!'
    """
}
workflow {
    TEST_RUN()
}

