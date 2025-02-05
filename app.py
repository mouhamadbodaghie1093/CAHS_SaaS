import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask

# Create a Flask server instance
server = Flask(__name__)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Login Page Layout
login_layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H2("CAHS_SaaS Login Page"),
                width={"size": 6, "offset": 3},
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Form(
                    [
                        dbc.Row(
                            dbc.Col(dbc.Label("Username", html_for="username"), width=12)
                        ),
                        dbc.Row(
                            dbc.Col(dbc.Input(id="username", placeholder="Enter Username", type="text"), width=12)
                        ),
                        dbc.Row(
                            dbc.Col(dbc.Label("Password", html_for="password"), width=12)
                        ),
                        dbc.Row(
                            dbc.Col(dbc.Input(id="password", placeholder="Enter Password", type="password"), width=12)
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Button("Login", id="login-button", color="primary", style={'width': '100%'}),
                                width=12
                            )
                        ),
                        html.Div(id="login-message",
                                 style={"color": "red", "textAlign": "center", "marginTop": "10px"}),
                    ]
                ),
                width={"size": 6, "offset": 3},
            )
        ),
    ]
)

# Main Page Layout (after successful login)
main_layout = html.Div(
    [
        html.H1("Welcome to the main page!"),
        html.Div("This page appears after successful login."),
        dbc.Button("Logout", id="logout-button", color="danger", style={"marginTop": "20px"}),
    ]
)

# Define the app layout, including a container to switch views
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # Handles URL changes
    html.Div(id="app-container", children=login_layout)  # Holds the active layout
])


# Define the login callback
@app.callback(
    [Output("app-container", "children"), Output("login-message", "children")],
    [Input("login-button", "n_clicks")],
    [State("username", "value"), State("password", "value")]
)
def login(n_clicks, username, password):
    if not n_clicks:
        return login_layout, ""

    if username == "cash" and password == "cash":
        return main_layout, ""  # Redirect to the main page
    else:
        return login_layout, "Invalid credentials, please try again."


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
