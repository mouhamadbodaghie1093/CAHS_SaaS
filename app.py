import base64
import gzip
import io
import os
import subprocess

import dash
import dash_bootstrap_components as dbc
from Bio import SeqIO
from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask

# Create a Flask server instance
server = Flask(__name__)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

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
                accept='.fastq.gz,.fasta.gz,.fasta, fastq'  # Support for .fastq.gz and .fasta.gz files
            ),
            html.Div(id='upload-message', className="mt-3"),
        ], width=6)
    ], className="justify-content-center mt-4"),

    # Data Visualization
    dbc.Row([
        dbc.Col(dcc.Graph(id='abundance-plot'), width=6),
        dbc.Col(dcc.Graph(id='density-plot'), width=6),
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
    html.H1("SNP Analysis Page", className="text-center mt-5"),
    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-3"),
])

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
     Output("download-zip", "data")],
    [Input("run-nextflow", "n_clicks")]
)
def run_nextflow(n_clicks):
    if not n_clicks:
        return "", dash.no_update

    script_path = os.path.abspath("bacteria_analysis.nf")

    if not os.path.exists(script_path):
        return f"Error: Nextflow script not found at {script_path}.", dash.no_update

    try:
        # Ensure results directory exists
        results_dir = os.path.join(os.getcwd(), "results")
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        # Run Nextflow pipeline
        result = subprocess.run(
            ["nextflow", "run", script_path],
            capture_output=True,
            text=True
        )

        # Capture both stdout and stderr for logging
        if result.returncode != 0:
            return f"Error running Nextflow:\n{result.stderr}\n{result.stdout}", dash.no_update

        # Path to the output ZIP file
        zip_file_path = os.path.join(results_dir, "output.zip")

        if not os.path.exists(zip_file_path):
            return f"Error: Nextflow finished, but no output file found at {zip_file_path}.", dash.no_update

        # Return status message and trigger download of the ZIP file
        return "Nextflow completed successfully!", dcc.send_file(zip_file_path)

    except Exception as e:
        return f"Unexpected error: {str(e)}", dash.no_update


# ----------------- HEALTH CHECK ROUTE ----------------- #
@server.route('/health')
def health_check():
    return "OK", 200


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run_server(debug=True)
