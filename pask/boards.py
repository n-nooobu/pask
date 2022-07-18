import os
from pathlib import Path
import json
import string
import random
import dash
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/boards')


DATA_DIR = Path(f'{os.path.dirname(__file__)}/data')
PREV_N1, PREV_N2 = 0, 0


def layout():
    global boards
    boards = []
    for json_path in DATA_DIR.glob('*.json'):
        if json_path.stem == 'category':
            continue
        board = dbc.Card(className='card_board', children=[
            dbc.CardBody([
                html.H4(json_path.stem),
                dbc.Button('Open', outline=True, color='warning', href=f'/board/{json_path.stem}')
            ])
        ])
        boards.append(board)
    boards.append(
        dbc.Button('+ Board', id='button-add-board', color='warning', className='button_add_board', n_clicks=0)
    )

    return dbc.Container(id='page', className='page', children=[
        html.Div(id='boards', children=boards),
        dbc.Modal(id='modal-add-board', is_open=False, children=[
            dbc.ModalBody([
                dbc.ModalTitle('Input board name.'),
                dbc.Input(id='input-board-name', className='card_board', type='text'),
                dbc.Button('Confirm', id='button-confirm-add-board', color='warning', n_clicks=0)
            ])
        ])
    ])


@dash.callback(
    Output('modal-add-board', 'is_open'),
    [Input('button-add-board', 'n_clicks'), Input('button-confirm-add-board', 'n_clicks')],
    [State('modal-add-board', 'is_open')],
    prevent_initial_call=True
)
def add_board_toggle_modal(n1, n2, is_open):
    global PREV_N1
    global PREV_N2
    if (n1 > PREV_N1) or (n2 > PREV_N2):
        is_open = not is_open
    PREV_N1, PREV_N2 = n1, n2
    return is_open


@dash.callback(
    [Output('boards', 'children'), Output('input-board-name', 'value')],
    [Input('button-confirm-add-board', 'n_clicks')],
    [State('input-board-name', 'value')],
    prevent_initial_call=True
)
def add_board(n_clicks, board_name):
    if n_clicks and board_name:
        json_path = DATA_DIR/f'{board_name}.json'
        if not json_path.exists():
            new_board = dbc.Card(className='card_board', children=[
                dbc.CardBody([
                    html.H4(board_name),
                    dbc.Button('Open', outline=True, color='warning', href=f'/board/{board_name}')
                ])
            ])
            boards.insert(-1, new_board)
            
            board_template = {
                'id': ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(24)]),
                'name': board_name,
                'list_data': {},
                'card_data': {},
                'entry_data': {},
                'list': [],
                'card': {},
                'entry': {},
            }
            with open(DATA_DIR/f'{board_name}.json', 'w', encoding='utf-8') as f:
                json.dump(board_template, f, ensure_ascii=False, indent=4)
        
    return boards, ''
