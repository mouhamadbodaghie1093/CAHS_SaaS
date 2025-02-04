import dash
import dash_bootstrap_components as dbc
from dash import html
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
                html.H2("Login Page"),
                width={"size": 6, "offset": 3},
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Form(
                    [
                        dbc.FormGroup(
                            [
                                dbc.Label("Username"),
                                dbc.Input(id="username", placeholder="Enter Username", type="text"),
                            ]
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Password"),
                                dbc.Input(id="password", placeholder="Enter Password", type="password"),
                            ]
                        ),
                        dbc.Button("Login", id="login-button", color="primary", block=True),
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
        # Your existing Dash components for the main page here
    ]
)

# Define the app layout initially as the login page
app.layout = login_layout


# Define the login callback to verify username and password
@app.callback(
    Output("app-container", "children"),
    [Input("login-button", "n_clicks")],
    [State("username", "value"), State("password", "value")]
)
def login(n_clicks, username, password):
    if n_clicks is None:
        return login_layout

    # Check if the credentials match
    if username == "cash" and password == "cash":
        return main_layout  # Redirect to the main page
    else:
        return html.Div([
            html.H3("Invalid credentials, please try again."),
            login_layout
        ])  # Keep the login page if invalid credentials


# Run the app on the server
if __name__ == "__main__":
    app.run_server(debug=True)
