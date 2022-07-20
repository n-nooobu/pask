import dash
from dash import dcc, html
import dash_bootstrap_components as dbc


app = dash.Dash(
    title='Pask',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True, pages_folder='.'
)
app.config['suppress_callback_exceptions'] = True

header = dbc.Navbar(
    dbc.Container(fluid=True, children=[
        html.A(
            dbc.Row(
                dbc.Col(dbc.NavbarBrand(app.title, className='ms-2')),
                align='center',
                className='g-0',
            ),
            href='/',
            style={'textDecoration': 'none'},
        ),
        dbc.Row(className='flex-grow-1', children=[
            dbc.NavbarToggler(id='navbar-toggler'),
            dbc.Collapse(
                dbc.Nav(className='w-100', children=[
                    dbc.NavItem(dbc.NavLink('Boards', href='/boards', active='exact')),
                    dbc.NavItem(
                        dbc.NavLink('Timeline', href='/timeline', active='exact'),
                        className='me-auto',
                    ),
                    dbc.NavItem(dbc.NavLink('About', href='/about', active='exact')),
                ]),
                id='navbar-collapse',
                is_open=False,
                navbar=True,
            )
        ])
    ]),
    dark=True,
    color='dark',
    fixed='top',
)

content = html.Div(id='page-content', children=[dash.page_container])

app.layout = html.Div(
    [dcc.Location(id='url'), header, content]
)


if __name__ == '__main__':
    app.run_server(debug=True, port=9453)
