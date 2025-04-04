import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

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
                html.Div(id="login-status", className="text-success text-center mt-3"),  # Add login-status div here
            ]),
            width=4,
        ),
        className="justify-content-center"
    ),
], fluid=True)

# Layout for the main page after login with analysis selection
analysis_selection_layout = html.Div([
    html.H2("Select Analysis Type", style={'color': '#2C3E50', 'marginTop': '20px'}),

    html.Div([
        html.Button('SNP Analysis', id='snp-analysis', n_clicks=0,
                    style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px'}),
        html.Button('Bacteria Analysis', id='bacteria-analysis', n_clicks=0,
                    style={'backgroundColor': '#3498DB', 'color': 'white', 'padding': '10px', 'marginLeft': '20px'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Placeholder for the selected analysis page
    html.Div(id='analysis-page-container')
])

# Layout for SNP Analysis page
snp_analysis_layout = html.Div([
    html.H2("SNP Analysis Page", style={'color': '#2C3E50', 'marginTop': '20px'}),
    html.Div([
        html.Label("Upload FNA File:", style={'fontWeight': 'bold'}),
        dcc.Upload(
            id='upload-fna',
            children=html.Button('Upload FNA File', style={'backgroundColor': '#3498DB', 'color': 'white'}),
            multiple=False
        ),
        html.Div(id='fna-file-name', style={'marginTop': '10px', 'color': '#2E86C1'}),
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Label("Upload BAM File:", style={'fontWeight': 'bold'}),
        dcc.Upload(
            id='upload-bam',
            children=html.Button('Upload BAM File', style={'backgroundColor': '#3498DB', 'color': 'white'}),
            multiple=False
        ),
        html.Div(id='bam-file-name', style={'marginTop': '10px', 'color': '#2E86C1'}),
    ], style={'marginBottom': '20px'}),

    html.Button('Run SNP Analysis', id='run-snp-analysis', n_clicks=0,
                style={'backgroundColor': '#E74C3C', 'color': 'white', 'fontSize': '16px', 'padding': '10px'}),

    html.Div([
        daq.Indicator(id="status-indicator", value=False, color="green"),
        html.Div(id='analysis-status', style={'marginTop': '10px', 'fontWeight': 'bold', 'color': '#27AE60'}),
    ], style={'marginTop': '20px'}),

    dcc.Download(id="download-vcf")
])

# Layout for Bacteria Analysis page (for future expansion)
bacteria_analysis_layout = html.Div([
    html.H2("Bacteria Analysis Page", style={'color': '#2C3E50', 'marginTop': '20px'}),
    html.P("This is a placeholder for the Bacteria Analysis. Implement similar logic to SNP analysis here.")
])


# ---------------- CALLBACKS ---------------- #

# Callback to handle login
@app.callback(
    [Output('login-message', 'children'),
     Output('login-status', 'children'),
     Output('url', 'href')],  # This will trigger the redirection
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value')
)
def handle_login(n_clicks, username, password):
    if n_clicks is None:
        return '', '', dash.no_update

    if username == 'admin' and password == 'password':  # Replace with your credentials
        return '', "Login successful. Redirecting to analysis selection page...", '/select-analysis'  # Redirect to analysis selection
    else:
        return "Invalid username or password.", '', dash.no_update


# Callback to display the correct page based on URL
@app.callback(
    Output("app-container", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/login":
        return login_layout
    elif pathname == "/select-analysis":
        return analysis_selection_layout
    elif pathname == "/snp-analysis":
        return snp_analysis_layout
    elif pathname == "/bacteria-analysis":
        return bacteria_analysis_layout
    else:
        return login_layout  # Default to login page


# Callback to navigate to SNP or Bacteria Analysis page
@app.callback(
    Output('analysis-page-container', 'children'),
    Input('snp-analysis', 'n_clicks'),
    Input('bacteria-analysis', 'n_clicks')
)
def display_analysis_page(snp_n_clicks, bacteria_n_clicks):
    if snp_n_clicks > 0:
        return dcc.Location(id='url', href='/snp-analysis')  # Redirect to SNP analysis page
    elif bacteria_n_clicks > 0:
        return dcc.Location(id='url', href='/bacteria-analysis')  # Redirect to Bacteria analysis page
    return dash.no_update


# Callback to handle SNP analysis (upload FNA, BAM files, run SNP analysis)
@app.callback(
    [Output('analysis-status', 'children'),
     Output('status-indicator', 'value'),
     Output('download-vcf', 'data')],
    Input('run-snp-analysis', 'n_clicks'),
    [State('upload-fna', 'contents'),
     State('upload-bam', 'contents')],
    prevent_initial_call=True
)
def run_snp_analysis(n_clicks, fna_contents, bam_contents):
    if not fna_contents or not bam_contents:
        return "Please upload both files before running analysis.", False, dash.no_update

    # Simulate SNP analysis (In a real scenario, integrate actual SNP processing)
    vcf_content = """##fileformat=VCFv4.2
#CHROM POS ID REF ALT QUAL FILTER INFO
chr1 101 . A G 100 PASS .
chr1 102 . T C 100 PASS .
"""
    vcf_file_path = 'snp_analysis_results.vcf'
    with open(vcf_file_path, 'w') as vcf_file:
        vcf_file.write(vcf_content)

    return "SNP analysis completed. Download the VCF file.", True, dcc.send_file(vcf_file_path)


# Set the initial layout (login page)
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),  # Add this component for URL management
    html.Div(id='app-container')  # Placeholder for page content
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
