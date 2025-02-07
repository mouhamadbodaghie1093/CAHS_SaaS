import os
import subprocess

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask, send_file

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
            html.Div(id="nextflow-status", className="text-center mt-3")
        ], width=4)
    ], className="justify-content-center mt-4"),

    # Button to download the result
    dbc.Row([
        dbc.Col([
            dbc.Button("Download Results", id="download-results", color="primary", className="d-block mx-auto mt-3",
                       disabled=True),
            html.Div(id="download-link", className="mt-3")
        ], width=4)
    ], className="justify-content-center mt-4"),

    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-4"),
], fluid=True)

# ----------------- PAGE ROUTING ----------------- #
pages = {
    "/menu": menu_layout,
    "/bacteria": bacteria_analysis_layout,
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
    Output("download-results", "disabled"),
    Output("download-link", "children"),
    [Input("run-nextflow", "n_clicks")]
)
def run_nextflow(n_clicks):
    if not n_clicks:
        return "", dash.no_update, True, ""

    script_path = os.path.abspath("bacteria_analysis.nf")

    # Check if script exists
    if not os.path.exists(script_path):
        return f"Error: Nextflow script not found at {script_path}.", dash.no_update, True, ""

    try:
        result = subprocess.run(
            ["nextflow", "run", script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"Error running Nextflow:\n{result.stderr}", dash.no_update, True, ""

        success_message = [line for line in result.stdout.splitlines() if "✔" in line]
        if success_message:
            # Check if results directory and plot file exist
            result_dir = os.path.join(os.getcwd(), "results")
            if os.path.exists(result_dir):
                files_in_result = os.listdir(result_dir)
                if "abundance_plot.png" in files_in_result:
                    # Create a download link for the results
                    download_url = "/download/results/abundance_plot.png"
                    return f"Nextflow completed successfully: {success_message[-1]}", {
                        'data': [{
                            'x': [0, 1, 2],  # Replace with actual data from your plot
                            'y': [2, 4, 8],  # Replace with actual data from your plot
                            'type': 'scatter',
                            'mode': 'lines+markers',
                            'name': 'Abundance'
                        }],
                        'layout': {
                            'title': 'Abundance Plot'
                        }
                    }, False, html.A("Click here to download the result", href=download_url, target="_blank")
                else:
                    return f"Nextflow completed, but no 'abundance_plot.png' found.", dash.no_update, True, ""
            else:
                return f"Nextflow completed, but 'results' directory is missing.", dash.no_update, True, ""

        return f"Nextflow Output:\n{result.stdout}", dash.no_update, True, ""
    except Exception as e:
        return f"Unexpected error: {str(e)}", dash.no_update, True, ""


# ----------------- DOWNLOAD RESULTS ----------------- #
@app.server.route("/download/results/<filename>")
def download_file(filename):
    result_dir = os.path.join(os.getcwd(), "results")
    return send_file(os.path.join(result_dir, filename), as_attachment=True)

# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    app.run_server(debug=True)
