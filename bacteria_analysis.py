import os
import subprocess

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask

# Create a Flask server instance
server = Flask(__name__)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ----------------- BACTERIA ANALYSIS PAGE ----------------- #
bacteria_analysis_layout = dbc.Container([
    html.H1("Bacteria Analysis", className="text-center mt-5"),
    dcc.Upload(
        id="upload-data",
        children=html.Button("Upload CSV File", className="btn btn-primary mt-3"),
        multiple=False,
    ),
    html.Div(id="file-name", className="text-center mt-2"),
    html.Div(id="data-table"),
    dcc.Graph(id="density-plot"),
    dbc.Button("Run Nextflow Analysis", id="run-nextflow", color="success", className="mt-3"),
    html.Div(id="nextflow-output", className="text-center mt-2"),
    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-3"),
], fluid=True)


# ----------------- CALLBACKS ----------------- #
@app.callback(
    [Output("file-name", "children"), Output("data-table", "children"), Output("density-plot", "figure")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")]
)
def process_uploaded_file(contents, filename):
    if contents is None:
        return "", "", px.scatter()

    # Simulating file save & read (for simplicity, assuming CSV format)
    file_path = f"./uploads/{filename}"
    os.makedirs("./uploads", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(contents.split(",")[-1])

    df = pd.read_csv(file_path)

    # Create density plot
    fig = px.histogram(df, x=df.columns[1], title="Bacteria Abundance Density")

    return f"Uploaded: {filename}", dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True), fig


@app.callback(
    Output("nextflow-output", "children"),
    [Input("run-nextflow", "n_clicks")]
)
def run_nextflow(n_clicks):
    if not n_clicks:
        return ""

    try:
        result = subprocess.run(["nextflow", "run", "bacteria_analysis.nf"], capture_output=True, text=True)
        return f"Nextflow Output:\n{result.stdout}"
    except Exception as e:
        return f"Error running Nextflow: {str(e)}"


# ----------------- ADD TO EXISTING DASH APP ----------------- #
existing_pages = {"/bacteria": bacteria_analysis_layout}


def display_page(pathname):
    return existing_pages.get(pathname, login_layout)


app.layout = html.Div([dcc.Location(id="url", refresh=False), html.Div(id="app-container")])


@app.callback(Output("app-container", "children"), [Input("url", "pathname")])
def update_page(pathname):
    return display_page(pathname)


# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    app.run_server(debug=True)
