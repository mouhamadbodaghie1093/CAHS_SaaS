import base64
import os
import subprocess

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import dcc, html
from dash.dependencies import Input, Output, State

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SNP_SCRIPT_PATH = os.path.join(BASE_DIR, "snp_analysis.nf")
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define the paths for uploaded files
UPLOAD_DIR = "/tmp"
FNA_FILE_PATH = os.path.join(UPLOAD_DIR, "uploaded_file.fna")
BAM_FILE_PATH = os.path.join(UPLOAD_DIR, "uploaded_file.bam")
REFERENCE_FILE_PATH = "/path/to/your/reference/file.fasta"
VCF_FILE_PATH = os.path.join(UPLOAD_DIR, "snp_analysis_results.vcf")

# ---------------- LOGIN PAGE ---------------- #
login_layout = dbc.Container([
    html.H2("CAHS_SaaS Login Page", className="text-center mt-5"),
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

# ---------------- ANALYSIS SELECTION PAGE ---------------- #
analysis_selection_layout = html.Div([
    html.H2("Select Analysis Type", style={'color': '#2C3E50', 'marginTop': '20px'}),
    html.Div([
        html.Button('SNP Analysis', id='snp-analysis', n_clicks=0,
                    style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px'}),
        html.Button('Bacteria Analysis', id='bacteria-analysis', n_clicks=0,
                    style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px', 'marginLeft': '20px'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),
    html.Div(id='analysis-page-container')  # Placeholder for the selected analysis page
])

# ---------------- SNP ANALYSIS PAGE ---------------- #
snp_analysis_layout = html.Div([
    html.H2("SNP Analysis", style={'color': '#2C3E50', 'marginTop': '20px'}),

    # Upload FNA file
    html.Label("Upload FNA File:", style={'fontWeight': 'bold'}),
    dcc.Upload(id='upload-fna', children=html.Button('Upload FNA File'), multiple=False),
    html.Div(id='fna-file-name', style={'marginTop': '10px', 'color': '#2E86C1'}),

    # Upload BAM file
    html.Label("Upload BAM File:", style={'fontWeight': 'bold', 'marginTop': '20px'}),
    dcc.Upload(id='upload-bam', children=html.Button('Upload BAM File'), multiple=False),
    html.Div(id='bam-file-name', style={'marginTop': '10px', 'color': '#2E86C1'}),

    # Run analysis button
    html.Button('Run SNP Analysis', id='run-snp-analysis', n_clicks=0,
                style={'backgroundColor': '#E74C3C', 'color': 'white', 'fontSize': '16px', 'padding': '10px'}),

    # Status indicator
    daq.Indicator(id="status-indicator", value=False, color="green"),
    html.Div(id='analysis-status', style={'marginTop': '10px', 'fontWeight': 'bold', 'color': '#27AE60'}),

    # Download result
    dcc.Download(id="download-vcf"),
])


# ---------------- CALLBACKS ---------------- #

# Handle login
@app.callback(
    Output('app-container', 'children'),
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if username == 'admin' and password == 'password':  # Replace with actual authentication
        return analysis_selection_layout
    else:
        return login_layout


# Display the correct page
@app.callback(
    Output('analysis-page-container', 'children'),
    [Input('snp-analysis', 'n_clicks'),
     Input('bacteria-analysis', 'n_clicks')]
)
def display_analysis_page(snp_n_clicks, bacteria_n_clicks):
    if snp_n_clicks > 0:
        return snp_analysis_layout
    elif bacteria_n_clicks > 0:
        return html.P("Bacteria Analysis - Coming Soon!")
    return dash.no_update


# Handle file uploads
def save_uploaded_file(contents, filename, file_path):
    """ Decode base64-encoded file content and save it to disk. """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    with open(file_path, 'wb') as file:
        file.write(decoded)
    return filename

@app.callback(
    Output('fna-file-name', 'children'),
    Input('upload-fna', 'contents'),
    State('upload-fna', 'filename'),
    prevent_initial_call=True
)
def upload_fna(contents, filename):
    return f"Uploaded: {save_uploaded_file(contents, filename, FNA_FILE_PATH)}"

@app.callback(
    Output('bam-file-name', 'children'),
    Input('upload-bam', 'contents'),
    State('upload-bam', 'filename'),
    prevent_initial_call=True
)
def upload_bam(contents, filename):
    return f"Uploaded: {save_uploaded_file(contents, filename, BAM_FILE_PATH)}"


# Run SNP analysis
@app.callback(
    [Output('analysis-status', 'children'),
     Output('status-indicator', 'value'),
     Output('download-vcf', 'data')],
    Input('run-snp-analysis', 'n_clicks'),
    prevent_initial_call=True
)
def run_snp_analysis(n_clicks):
    if not os.path.exists(FNA_FILE_PATH) or not os.path.exists(BAM_FILE_PATH):
        return "Please upload both files before running analysis.", False, dash.no_update

    # Run Nextflow
    nextflow_cmd = f"nextflow run snp_analysis.nf --fna {FNA_FILE_PATH} --bam {BAM_FILE_PATH}"

    try:
        result = subprocess.run(
            nextflow_cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout = result.stdout.decode()
        stderr = result.stderr.decode()

        print("STDOUT:\n", stdout)
        print("STDERR:\n", stderr)

        # Hardcoded path (adjust or make dynamic)
        vcf_path = "snp_analysis_results.vcf"

        if os.path.exists(vcf_path):
            return "SNP analysis complete. Downloading VCF file...", True, dcc.send_file(vcf_path)
        else:
            return f"SNP analysis finished, but VCF file not found at expected location: {vcf_path}", False, dash.no_update

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode() if e.stderr else "No stderr captured"
        stdout_output = e.stdout.decode() if e.stdout else "No stdout captured"
        print("Exception STDOUT:\n", stdout_output)
        print("Exception STDERR:\n", stderr_output)
        return f"Error running SNP analysis:\n{stderr_output}", False, dash.no_update

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}", False, dash.no_update



# Set initial layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='app-container', children=login_layout)
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8060)
