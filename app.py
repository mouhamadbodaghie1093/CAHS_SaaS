import base64
import os
import subprocess
import uuid

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import dcc, html, Input, Output, State, ctx
from dash.exceptions import PreventUpdate

# Constants
UPLOAD_ROOT = "/tmp"

# Dash App Initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Login Layout
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

# SNP Analysis Layout
snp_analysis_layout = html.Div([
    dcc.Store(id='session-dir-store', storage_type='session'),

    html.H2("SNP Analysis", style={'color': '#2C3E50', 'marginTop': '20px'}),

    html.Label("Upload FNA File:", style={'fontWeight': 'bold'}),
    dcc.Upload(id='upload-fna', children=html.Button('Upload FNA File'), multiple=False),
    html.Div(id='fna-file-name', style={'marginTop': '10px', 'color': '#2E86C1'}),

    html.Label("Upload BAM File:", style={'fontWeight': 'bold', 'marginTop': '20px'}),
    dcc.Upload(id='upload-bam', children=html.Button('Upload BAM File'), multiple=False),
    html.Div(id='bam-file-name', style={'marginTop': '10px', 'color': '#2E86C1'}),

    html.Button('Run SNP Analysis', id='run-snp-analysis', n_clicks=0,
                style={'backgroundColor': '#E74C3C', 'color': 'white', 'fontSize': '16px', 'padding': '10px'}),

    daq.Indicator(id="status-indicator", value=False, color="green"),
    html.Div(id='analysis-status', style={'marginTop': '10px', 'fontWeight': 'bold', 'color': '#27AE60'}),

    dcc.Download(id="download-vcf"),
])

# Analysis Selection Layout
analysis_selection_layout = html.Div([
    html.H2("Select Analysis Type", style={'color': '#2C3E50', 'marginTop': '20px'}),
    html.Div([
        html.Button('SNP Analysis', id='snp-analysis', n_clicks=0,
                    style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px'}),
        html.Button('Bacteria Analysis', id='bacteria-analysis', n_clicks=0,
                    style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px', 'marginLeft': '20px'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),
    html.Div(id='analysis-page-container')
])

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-dir-store', storage_type='session'),
    html.Div(id='app-container', children=login_layout)
])


# -------------------------------- CALLBACKS -------------------------------- #

@app.callback(
    Output('app-container', 'children'),
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    # Simple hardcoded login check
    if username == 'admin' and password == 'password':
        return analysis_selection_layout
    return login_layout

@app.callback(
    Output('analysis-page-container', 'children'),
    Input('snp-analysis', 'n_clicks'),
    Input('bacteria-analysis', 'n_clicks'),
)
def display_analysis_page(snp_clicks, bacteria_clicks):
    triggered = ctx.triggered_id
    if triggered == 'snp-analysis':
        return snp_analysis_layout
    elif triggered == 'bacteria-analysis':
        return html.P("Bacteria Analysis - Coming Soon!")
    raise PreventUpdate


@app.callback(
    Output('session-dir-store', 'data'),
    Input('analysis-page-container', 'children'),
    prevent_initial_call=True
)
def init_session(_):
    # Create a unique session directory for uploads and outputs
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def save_file(contents, path):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    with open(path, 'wb') as f:
        f.write(decoded)

@app.callback(
    Output('fna-file-name', 'children'),
    Input('upload-fna', 'contents'),
    State('upload-fna', 'filename'),
    State('session-dir-store', 'data'),
    prevent_initial_call=True
)
def handle_fna_upload(contents, filename, session_dir):
    if not contents:
        raise PreventUpdate
    path = os.path.join(session_dir, filename)
    save_file(contents, path)
    return f"Uploaded: {filename}"

@app.callback(
    Output('bam-file-name', 'children'),
    Input('upload-bam', 'contents'),
    State('upload-bam', 'filename'),
    State('session-dir-store', 'data'),
    prevent_initial_call=True
)
def handle_bam_upload(contents, filename, session_dir):
    if not contents:
        raise PreventUpdate
    path = os.path.join(session_dir, filename)
    save_file(contents, path)
    return f"Uploaded: {filename}"

@app.callback(
    [Output('analysis-status', 'children'),
     Output('status-indicator', 'value'),
     Output('download-vcf', 'data')],
    Input('run-snp-analysis', 'n_clicks'),
    State('session-dir-store', 'data'),
    prevent_initial_call=True
)
def run_snp_analysis(n_clicks, session_dir):
    if not session_dir or not os.path.exists(session_dir):
        return "Session directory not found.", False, dash.no_update

    fna_files = [f for f in os.listdir(session_dir) if f.endswith('.fna')]
    bam_files = [f for f in os.listdir(session_dir) if f.endswith('.bam')]

    if not fna_files or not bam_files:
        return "Missing FNA or BAM file.", False, dash.no_update

    fna_path = os.path.join(session_dir, fna_files[0])
    bam_path = os.path.join(session_dir, bam_files[0])

    try:
        nextflow_cmd = (
            f"/usr/local/bin/nextflow run /home/mouhamadbodaghie/PycharmProjects/CAHS_SaaS/snp_analysis.nf "
            f"--reference {fna_path} --bam {bam_path} --outdir {session_dir}"
        )
        result = subprocess.run(
            nextflow_cmd, shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        print(result.stdout.decode())  # For debugging
        print(result.stderr.decode())

        vcf_files = [f for f in os.listdir(session_dir) if f.endswith(".vcf")]
        if vcf_files:
            vcf_path = os.path.join(session_dir, vcf_files[0])
            return "SNP analysis complete. Click to download.", True, dcc.send_file(vcf_path)
        else:
            return "VCF output not found.", False, dash.no_update
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode() if e.stderr else str(e)
        return f"Nextflow error:\n{error_output}", False, dash.no_update


# -------------------------------- MAIN -------------------------------- #

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8060)
