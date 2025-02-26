import base64
import io
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

    # File Upload
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id="upload-data",
                children=html.Button("Upload CSV File", className="btn btn-primary mt-3"),
                multiple=False,
            ),
            html.Div(id="file-name", className="text-center mt-2"),
        ], width=6)
    ], className="justify-content-center mt-4"),

    # Display Data Table and Plot
    dbc.Row([
        dbc.Col(html.Div(id="data-table"), width=6),
        dbc.Col(dcc.Graph(id="density-plot"), width=6),
    ], className="mt-4"),

    # Run Nextflow Button
    dbc.Row([
        dbc.Col([
            dbc.Button("Run Nextflow Analysis", id="run-nextflow", color="success", className="mt-3 d-block mx-auto"),
            html.Div(id="nextflow-output", className="text-center mt-2"),
        ], width=6)
    ], className="justify-content-center mt-4"),

    # Back Button
    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-4"),
], fluid=True)


# ----------------- CALLBACKS ----------------- #
@app.callback(
    [Output("file-name", "children"), Output("data-table", "children"), Output("density-plot", "figure")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")]
)
def process_uploaded_file(contents, filename):
    if contents is None:
        return "", "", px.scatter(title="No Data Available")

    try:
        # Decode base64 CSV content
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

        # Create a density plot using the first numerical column
        numeric_columns = df.select_dtypes(include=["number"]).columns
        if numeric_columns.empty:
            return f"Uploaded: {filename} (No numeric data found)", dbc.Table.from_dataframe(df.head(), striped=True,
                                                                                             bordered=True,
                                                                                             hover=True), px.scatter(
                title="No Numeric Data")

        fig = px.histogram(df, x=numeric_columns[0], title=f"Bacteria Abundance Density ({numeric_columns[0]})")

        return f"Uploaded: {filename}", dbc.Table.from_dataframe(df.head(), striped=True, bordered=True,
                                                                 hover=True), fig

    except Exception as e:
        return f"Error processing file: {str(e)}", "", px.scatter(title="Error Processing Data")


@app.callback(
    Output("nextflow-output", "children"),
    [Input("run-nextflow", "n_clicks")]
)
def run_nextflow(n_clicks):
    if not n_clicks:
        return ""

    try:
        script_path = os.path.abspath("bacteria_analysis.nf")

        if not os.path.exists(script_path):
            return f"Error: Nextflow script not found at {script_path}"

        result = subprocess.run(["nextflow", "run", script_path], capture_output=True, text=True)

        if result.returncode != 0:
            return f"Error running Nextflow:\n{result.stderr}"

        return f"Nextflow Output:\n{result.stdout}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"


# ----------------- PAGE ROUTING ----------------- #
pages = {
    "/bacteria": bacteria_analysis_layout,
}

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="app-container")
])


@app.callback(Output("app-container", "children"), [Input("url", "pathname")])
def display_page(pathname):
    return pages.get(pathname, html.H2("Page Not Found"))  # Default error page


# ---------------- RUN APP ----------------- #
if __name__ == "__main__":
    app.run_server(debug=True)
