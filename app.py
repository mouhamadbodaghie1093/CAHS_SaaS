import logging

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html

logging.basicConfig(level=logging.INFO)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Dummy function to simulate loading data
def load_data():
    data = {
        'sample_id': ['sample_001', 'sample_002'],
        'tax': ['Bacteria A', 'Bacteria B'],
        'relative_abundance_percent': [40, 60],
    }
    return pd.DataFrame(data)


# Load data
merged_data = load_data()

# Define the layout
app.layout = html.Div([
    html.H1("Bacteria Analysis Dashboard"),
    dcc.Graph(
        id='abundance-graph',
        figure=px.bar(
            merged_data,
            x='sample_id',
            y='relative_abundance_percent',
            color='tax',
            title='Relative Abundance Percent by Sample',
            barmode='stack'
        )
    ),
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
