#!/usr/bin/env nextflow

process zipOutput {
    output:
    file 'output.zip' into zip_output  // Ensure output is tracked

    script:
    """
    mkdir -p results
    echo -e "sample_ID\\tabundance\\tdensity" > results/abundance_table_species.tsv
    echo -e "Sample1\\t10.5\\t0.8" >> results/abundance_table_species.tsv
    echo -e "Sample2\\t15.2\\t1.2" >> results/abundance_table_species.tsv
    echo -e "Sample3\\t9.8\\t0.5" >> results/abundance_table_species.tsv

    # Generate a plot using a separate Python script
    python3 - <<END
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.read_csv('results/abundance_table_species.tsv', sep='\\t')
    df.plot(kind='bar', x='sample_ID', y='abundance')
    plt.savefig('results/abundance_plot.png')
    END

    # Create a ZIP file with the output files
    zip -r output.zip results/*
    """
}

workflow {
    zipOutput()  // Execute the process
}
