process zipOutput {
    output:
    file 'output.zip' into outputChannel

    script:
    """
    # Set working directory to a known path
    mkdir -p \$PWD/results

    # Create example data files
    echo -e "sample_ID\tabundance\tdensity" > \$PWD/results/abundance_table_species.tsv
    echo -e "Sample1\t10.5\t0.8" >> \$PWD/results/abundance_table_species.tsv
    echo -e "Sample2\t15.2\t1.2" >> \$PWD/results/abundance_table_species.tsv
    echo -e "Sample3\t9.8\t0.5" >> \$PWD/results/abundance_table_species.tsv

    # Create a plot (for example using matplotlib)
    python3 -c "import matplotlib.pyplot as plt;
    import pandas as pd;
    df = pd.read_csv('\$PWD/results/abundance_table_species.tsv', sep='\\t');
    df.plot(kind='bar', x='sample_ID', y='abundance');
    plt.savefig('\$PWD/results/abundance_plot.png')"

    # Create a ZIP file containing the output files
    cd \$PWD/results
    zip -r output.zip abundance_table_species.tsv abundance_plot.png
    """
}

workflow {
    zipOutput()
}
