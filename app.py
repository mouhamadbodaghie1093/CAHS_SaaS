import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from flask import Flask

# Create a Flask server instance
server = Flask(__name__)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ---------------- LOGIN PAGE ---------------- #
login_layout = dbc.Container([
    html.H2("CAHS_SaaS Login Page", className="text-center mt-5"),
    dbc.Row(
        dbc.Col(
            dbc.Form(
                [
                    dbc.Label("Username", html_for="username"),
                    dbc.Input(id="username", placeholder="Enter Username", type="text", className="mb-3"),
                    dbc.Label("Password", html_for="password"),
                    dbc.Input(id="password", placeholder="Enter Password", type="password", className="mb-3"),
                    dbc.Button("Login", id="login-button", color="primary", className="w-100"),
                    html.Div(id="login-message", className="text-danger text-center mt-3"),
                ]
            ),
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

# ----------------- PLACEHOLDER PAGES ----------------- #
bacteria_analysis_layout = dbc.Container([
    html.H1("Bacteria Analysis Page", className="text-center mt-5"),
    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-3"),
])

snp_analysis_layout = dbc.Container([
    html.H1("SNP Analysis Page", className="text-center mt-5"),
    dbc.Button("Back to Menu", href="/menu", color="secondary", className="d-block mx-auto mt-3"),
])

# ----------------- APP LAYOUT ----------------- #
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # Handles URL changes
    html.Div(id="app-container")  # Holds active page
])


# ----------------- CALLBACKS ----------------- #
@app.callback(
    Output("url", "pathname"),
    [Input("login-button", "n_clicks")],
    [State("username", "value"), State("password", "value")]
)
def login(n_clicks, username, password):
    if n_clicks and username == "cash" and password == "cash":
        return "/menu"  # Redirect to menu page
    return dash.no_update  # No change if login fails


@app.callback(
    Output("app-container", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/menu":
        return menu_layout
    elif pathname == "/bacteria":
        return bacteria_analysis_layout
    elif pathname == "/snp":
        return snp_analysis_layout
    return login_layout  # Default to login page


# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    app.run_server(debug=True)
