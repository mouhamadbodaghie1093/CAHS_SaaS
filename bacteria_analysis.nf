#!/usr/bin/env nextflow

process zipOutput {

    output:
    file 'output.zip' into zip_output  // Make sure the output is tracked

    script:
    """
    mkdir -p /home/mouhamadbodaghie/PycharmProjects/CAHS_SaaS/results
    # Create some example data files
    echo -e "sample_ID\tabundance\tdensity" > abundance_table_species.tsv
    echo -e "Sample1\t10.5\t0.8" >> abundance_table_species.tsv
    echo -e "Sample2\t15.2\t1.2" >> abundance_table_species.tsv
    echo -e "Sample3\t9.8\t0.5" >> abundance_table_species.tsv

    # Create a plot (for example using matplotlib)
    python3 -c "import matplotlib.pyplot as plt;
    import pandas as pd;
    df = pd.read_csv('abundance_table_species.tsv', sep='\\t');
    df.plot(kind='bar', x='sample_ID', y='abundance');
    plt.savefig('abundance_plot.png')"

    # Create a ZIP file containing the output files
    zip -r /home/mouhamadbodaghie/PycharmProjects/CAHS_SaaS/results/output.zip abundance_table_species.tsv abundance_plot.png
    """
}

workflow {
    zipOutput()  // Run the 'zipOutput' process
}
