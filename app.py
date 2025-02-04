import base64
import os

import dash
import pandas as pd
from asgiref.wsgi import WsgiToAsgi
from dash import dcc, html, Input, Output, State, dash_table
from flask import Flask

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize Dash app
app = dash.Dash(__name__, server=flask_app, suppress_callback_exceptions=True)
server = flask_app  # Expose Flask server for Gunicorn
asgi_app = WsgiToAsgi(flask_app)  # Convert Flask to ASGI

# Layout of the web app
app.layout = html.Div([
    html.H1("FastQ File Processor"),
    dcc.Upload(
        id="upload-data",
        children=html.Button("Upload File"),
        multiple=False,
    ),
    html.Div(id="output-data-upload"),
])


# Callback to process uploaded file
@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(contents, filename):
    if contents is None:
        return "No file uploaded."

    try:
        # Decode file
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        # Save file temporarily
        temp_filename = f"temp_{filename}"
        with open(temp_filename, "wb") as f:
            f.write(decoded)

        # Process file (placeholder for real processing)
        result = pd.DataFrame({"Filename": [filename], "Status": ["Processed"]})

        # Remove temp file after processing
        os.remove(temp_filename)

        # Return results in a table
        return dash_table.DataTable(
            data=result.to_dict("records"),
            columns=[{"name": i, "id": i} for i in result.columns],
        )

    except Exception as e:
        # Handle errors
        return f"Error processing file: {str(e)}"


# Run app (for local testing)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(asgi_app, host="0.0.0.0", port=8080)
