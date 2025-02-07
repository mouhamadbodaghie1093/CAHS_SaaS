import os
import subprocess

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask

# Create a Flask server instance
server = Flask(__name__)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

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
                multiple=False
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


# Run Nextflow Pipeline
@app.callback(
    Output("nextflow-status", "children"),
    Output("abundance-plot", "figure"),
    [Input("run-nextflow", "n_clicks")]
)
def run_nextflow(n_clicks):
    if not n_clicks:
        return "", dash.no_update

    script_path = os.path.abspath("bacteria_analysis.nf")

    # Check if script exists
    if not os.path.exists(script_path):
        current_dir = os.getcwd()
        files_in_dir = os.listdir(current_dir)
        return f"Error: Nextflow script not found at {script_path}. Current Directory: {current_dir}. Files: {files_in_dir}", dash.no_update

    try:
        result = subprocess.run(
            ["nextflow", "run", script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"Error running Nextflow:\n{result.stderr}", dash.no_update

        success_message = [line for line in result.stdout.splitlines() if "✔" in line]
        if success_message:
            # Check if results directory and plot file exist
            result_dir = os.path.join(os.getcwd(), "results")
            if os.path.exists(result_dir):
                files_in_result = os.listdir(result_dir)
                if "abundance_plot.png" in files_in_result:
                    return f"Nextflow completed successfully: {success_message[-1]}", {
                        'data': [{
                            'x': [0, 1, 2],  # Replace with your dynamic data
                            'y': [2, 4, 8],  # Replace with your dynamic data
                            'type': 'scatter',
                            'mode': 'lines+markers',
                            'name': 'Abundance'
                        }],
                        'layout': {
                            'title': 'Abundance Plot'
                        }
                    }
                else:
                    # Simulate result for testing
                    return f"Nextflow completed, but no 'abundance_plot.png' found in the results directory. Files: {files_in_result}", {
                        'data': [{
                            'x': [0, 1, 2],  # Simulated Data
                            'y': [1, 2, 3],  # Simulated Data
                            'type': 'scatter',
                            'mode': 'lines+markers',
                            'name': 'Simulated Abundance'
                        }],
                        'layout': {
                            'title': 'Abundance Plot (Simulated)'
                        }
                    }
            else:
                return f"Nextflow completed, but 'results' directory is missing.", dash.no_update

        return f"Nextflow Output:\n{result.stdout}", dash.no_update
    except Exception as e:
        return f"Unexpected error: {str(e)}", dash.no_update


# ----------------- HEALTH CHECK ROUTE ----------------- #
@server.route('/health')
def health_check():
    return "OK", 200

# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run_server(debug=False, use_reloader=False)  # Disable reloader for production
