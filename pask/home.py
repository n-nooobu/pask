import dash
from dash import dcc, html, Input, Output, State
from dash.dependencies import ClientsideFunction
from dash_extensions.enrich import DashBlueprint
import dash_bootstrap_components as dbc



dash.register_page(__name__, path='/')


page_style = {
    'width': '1500px',
    'background-color': '#EBECF0',
    'margin-top': '5rem',
    'margin-left': '2rem',
    'margin-right': '2rem',
}


layout = html.Div(id="main", style=page_style, children=[
    html.P('aaaa')
])