import base64
import gzip
import io
import os
import subprocess

import dash
import dash_bootstrap_components as dbc
import numpy as np
from Bio import SeqIO
from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask

# Create a Flask server instance
server = Flask(__name__)
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.layout = html.Div([
    html.Button("Download VCF", id="download-button"),
    dcc.Download(id="download-link")
])

# ---------------- LOGIN PAGE ---------------- #
login_layout = dbc.Container([
    html.H2("CAHS_SaaS Login Page for Test", className="text-center mt-5"),
    dbc.Row(
        dbc.Col(
            dbc.Form([
                dbc.Label("Username", html_for="username"),
                dbc.Input(id="username", placeholder="Enter Username", type="text", className="mb-3"),
                dbc.Label("Password", html_for="password"),
                dbc.Input(id="password", placeholder="Enter Password", type="password", className="mb-3"),
                dbc.Button("Login", id="login-button", color="primary", className="w-100"),
                html.Div(id="login-message", className="text-danger text-center mt-3"),
            ]),
            width=4,
        ),
        className="justify-content-center"
    ),
], fluid=True)

# ---------------- MENU PAGE ---------------- #
menu_layout = dbc.Container([
    html.H2("Welcome to the CAHS_SaaS Platform", className="text-center mt-5"),
    html.P("Choose an analysis option below:", className="text-center"),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Bacteria Analysis", className="card-title text-center"),
                    html.P("Perform in-depth bacterial data analysis.", className="text-center"),
                    dbc.Button("Go to Bacteria Analysis", href="/bacteria", color="primary",
                               className="d-block mx-auto"),
                ]),
                className="shadow-lg",
            ),
            width=5
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("SNP Analysis", className="card-title text-center"),
                    html.P("Analyze SNP variations efficiently.", className="text-center"),
                    dbc.Button("Go to SNP Analysis", href="/snp", color="success", className="d-block mx-auto"),
                ]),
                className="shadow-lg",
            ),
            width=5
        ),
    ], className="justify-content-center mt-4"),

    dbc.Row(
        dbc.Col(
            dbc.Button("Logout", href="/", color="danger", className="mt-4 d-block mx-auto"),
            width=3
        ),
        className="justify-content-center"
    ),
], fluid=True)

# ----------------- BACTERIA ANALYSIS PAGE ----------------- #
bacteria_analysis_layout = dbc.Container([
    html.H1("Bacteria Analysis", className="text-center mt-5"),

    # File Upload
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Button('Upload Bacteria Data', className="btn btn-primary"),
                multiple=False,
                accept='.fastq.gz,.fasta.gz,.fasta, fastq,.fna'  # Support for .fastq.gz and .fasta.gz files
            ),
            html.Div(id='upload-message', className="mt-3"),
        ], width=6)
    ], className="justify-content-center mt-4"),

    # Data Visualization
    dbc.Row([
        dbc.Col(dcc.Graph(id='abundance-plot'), width=6),
        dbc.Col(dcc.Graph(id='shannon-plot'), width=6),
    ], className="mt-4"),

    # Run Nextflow Pipeline
    dbc.Row([
        dbc.Col([
            dbc.Button("Run Nextflow Analysis", id="run-nextflow", color="success", className="d-block mx-auto mt-3"),
            html.Div(id="nextflow-status", className="text-center mt-3")  # Updated Output ID
        ], width=4)
    ], className="justify-content-center mt-4"),

    # Download ZIP file
    dcc.Download(id="download-zip"),

    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-4"),
], fluid=True)

# ----------------- SNP ANALYSIS PAGE ----------------- #
snp_analysis_layout = dbc.Container([
    html.H1("SNP Analysis", className="text-center mt-5"),

    # File Upload Section for FASTQ Files
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-fastq-data',
                children=html.Button('Upload FASTQ File', className="btn btn-primary"),
                multiple=False,
                accept='.fastq,.fastq.gz,.fna'
            ),
            html.Div(id='upload-fastq-message', className="mt-3"),
        ], width=6)
    ], className="justify-content-center mt-4"),

    # File Upload Section for BAM Files
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-bam-data',
                children=html.Button('Upload BAM File', className="btn btn-primary"),
                multiple=False,
                accept='.bam'
            ),
            html.Div(id='upload-bam-message', className="mt-3"),
        ], width=6)
    ], className="justify-content-center mt-4"),

    # SNP Analysis Execution
    dbc.Row([
        dbc.Col([
            dbc.Button("Run SNP Analysis", id="run-snp-analysis", color="success", className="d-block mx-auto mt-3"),
            html.Div(id="snp-analysis-status", className="text-center mt-3")
        ], width=4)
    ], className="justify-content-center mt-4"),

    # Add Download VCF Button
    dbc.Row([
        dbc.Col([
            dbc.Button("Download VCF", id="download-vcf-button", color="info", className="d-block mx-auto mt-3"),
            dcc.Download(id="download-vcf")
        ], width=4)
    ], className="justify-content-center mt-4"),

    # Back Button
    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-4"),
], fluid=True)



@app.callback(
    [Output("upload-fastq-message", "children"),
     Output("upload-bam-message", "children"),
     Output("run-snp-analysis", "data")],
    [Input("upload-fastq-data", "contents"), Input("upload-bam-data", "contents")],
    [State("upload-fastq-data", "filename"), State("upload-bam-data", "filename")]
)
def handle_snp_file_upload(fastq_contents, bam_contents, fastq_filename, bam_filename):
    fastq_msg, fastq_file_path = save_uploaded_file(fastq_contents, fastq_filename) if fastq_contents else (None, None)
    bam_msg, bam_file_path = save_uploaded_file(bam_contents, bam_filename) if bam_contents else (None, None)

    # Only proceed with SNP analysis if both files are uploaded
    if fastq_file_path and bam_file_path:
        return fastq_msg, bam_msg, (fastq_file_path, bam_file_path)

    return fastq_msg or bam_msg, dash.no_update, dash.no_update


def save_uploaded_file(contents, filename):
    if contents is None:
        return "No file uploaded."

    data = contents.split(",")[1]
    decoded = base64.b64decode(data)

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(decoded)

    return f"File saved at {file_path}", file_path


# ----------------- PAGE ROUTING ----------------- #
pages = {
    "/menu": menu_layout,
    "/bacteria": bacteria_analysis_layout,
    "/snp": snp_analysis_layout
}

# Main layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # Handles URL changes
    html.Div(id="app-container")  # Holds active page content
])


# ----------------- CALLBACKS ----------------- #

# Login authentication
@app.callback(
    Output("url", "pathname"),
    [Input("login-button", "n_clicks")],
    [State("username", "value"), State("password", "value")]
)
def login(n_clicks, username, password):
    if n_clicks and username == "cash" and password == "cash":  # Consider replacing with a secure method
        return "/menu"  # Redirect to menu page
    return dash.no_update  # No change if login fails


# Page rendering based on URL
@app.callback(
    Output("app-container", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    return pages.get(pathname, login_layout)  # Default to login page if path is unknown


# Handle file upload and validate FASTA/FASTQ
@app.callback(
    Output("upload-message", "children"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")]
)
def handle_file_upload(contents, filename):
    if contents is None:
        return "Please upload a valid FASTA or FASTQ file."

    # Check if file extension is valid (support .gz extensions)
    file_extension = filename.split('.')[-2].lower() if filename.endswith('.gz') else filename.split('.')[-1].lower()

    if file_extension not in ['fasta', 'fastq']:
        return "Unsupported file format. Please upload FASTA or FASTQ."

    try:
        # Decode and parse file contents
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        file_io = io.BytesIO(decoded)

        # If gzipped file, decompress
        if filename.endswith(".gz"):
            with gzip.GzipFile(fileobj=file_io) as gz_file:
                file_content = gz_file.read().decode("utf-8")
                file_io = io.StringIO(file_content)  # Re-create file-like object for parsing

        # Parse FASTA or FASTQ files
        if file_extension == 'fasta':
            records = list(SeqIO.parse(file_io, "fasta"))
        elif file_extension == 'fastq':
            records = list(SeqIO.parse(file_io, "fastq"))

        if len(records) == 0:
            return "No sequences found in the uploaded file."

        # Return success message
        return f"File uploaded successfully, containing {len(records)} sequences."

    except Exception as e:
        return f"Error processing file: {str(e)}"


# Run Nextflow Pipeline
@app.callback(
    [Output("nextflow-status", "children"),
     Output("download-zip", "data"),
     Output("abundance-plot", "figure"),
     Output("shannon-plot", "figure")],
    [Input("run-nextflow", "n_clicks")]
)
def run_nextflow(n_clicks):
    if not n_clicks:
        return "", dash.no_update, dash.no_update, dash.no_update

    try:
        # Example nextflow command (adjust to your specific use case)
        command = ["nextflow", "run", "bacteria_analysis.nf", "--input", "input_dada.fastq"]
        subprocess.run(command, check=True)

        # Generate plots (placeholder)
        abundance_plot = {
            "data": [{"x": np.arange(10), "y": np.random.random(10), "type": "bar"}],
            "layout": {"title": "Abundance Plot"}
        }

        shannon_plot = {
            "data": [{"x": np.arange(10), "y": np.random.random(10), "type": "line"}],
            "layout": {"title": "Shannon Index Plot"}
        }

        # Generate zip file for download (placeholder path)
        zip_data = "path_to_your_zip_file.zip"

        return "Nextflow analysis complete.", dcc.send_file(zip_data), abundance_plot, shannon_plot

    except subprocess.CalledProcessError as e:
        return f"Nextflow pipeline failed: {str(e)}", dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output("snp-analysis-status", "children"),
    [Input("run-snp-analysis", "n_clicks")],
    [State("run-snp-analysis", "data")]
)
def run_snp_analysis(n_clicks, file_paths):
    if not n_clicks or not file_paths:
        return "Please upload both FASTQ and BAM files first."

    try:
        fastq_path, bam_path = file_paths
        command = ["nextflow", "run", "snp_analysis.nf", "--fna", fastq_path, "--bam", bam_path]
        subprocess.run(command, check=True)
        return "SNP Analysis complete."
    except subprocess.CalledProcessError as e:
        return f"SNP pipeline failed: {str(e)}"

    @app.callback(
        Output("download-vcf", "data"),
        Input("download-vcf-button", "n_clicks"),
        prevent_initial_call=True
    )
    def download_vcf(n_clicks):
        vcf_path = "/path/to/your/output.vcf"  # Ensure this file exists
        return dcc.send_file(vcf_path)


if __name__ == "__main__":
    app.run_server(debug=True)
