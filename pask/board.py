import os
from pathlib import Path
import json
import string
import random
from datetime import datetime, date, timezone, timedelta
import dash
from dash import dcc, html, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc


dash.register_page(__name__, path_template='/board/<board_name>')


DATA_DIR = Path(f'{os.path.dirname(__file__)}/data')
BOARD_DATA = None
PREV_N1, PREV_N2, PREV_N_ADD_LIST, PREV_N_CARD_TO_LEFT, PREV_N_CARD_TO_RIGHT = 0, 0, 0, 0, 0
PREV_N_ADD_CARD, PREV_N1_CARD, PREV_N2_CARD, PREV_N3_CARD = {}, {}, {}, {}
PREV_N_LIST_TO_LEFT, PREV_N_LIST_TO_RIGHT = None, None


def layout(board_name=None):
    global BOARD_DATA
    global PREV_N_LIST_TO_LEFT
    global PREV_N_LIST_TO_RIGHT

    if board_name:
        json_path = DATA_DIR/f'{board_name}.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            BOARD_DATA = json.load(f)

        lists = []
        all_modals = []
        list_ids = BOARD_DATA['list']
        for list_id in list_ids:
            list_data = BOARD_DATA['list_data'][list_id]
            card_ids = BOARD_DATA['card'][list_id]
            cards = []
            modals = []
            for card_id in card_ids:
                card_data = BOARD_DATA['card_data'][card_id]
                
                now = datetime.now(timezone.utc).astimezone()
                start = None
                if card_data['start'] is not None:
                    start = datetime.fromisoformat(card_data['start']).astimezone()
                due = None
                if card_data['due'] is not None:
                    due = datetime.fromisoformat(card_data['due']).astimezone()

                color = None
                if due is not None:
                    if now >= due:
                        color = 'danger'
                    elif timedelta(days=0) <= due - now <= timedelta(days=1):
                        color = 'warning'

                cards.append(
                    dbc.Card(id={'type': "card", 'index': card_id}, className='card', color=color, children=[
                        dbc.Row(justify="between", children=[
                            dbc.Col(width={"size": 'auto'}, children=[
                                dbc.CardBody(card_data['name']),
                            ]),
                            dbc.Col(width={"size": 'auto'}, children=[
                                dbc.Button("=", id={'type': "button-card-open-modal", 'index': card_id}, size="sm", color=None, n_clicks=0),
                            ]),
                        ])
                    ])
                )
                modals.append(
                    dbc.Modal(id={'type': "modal-card", 'index': card_id}, is_open=False, children=[
                        dbc.ModalBody([
                            html.H4('Name'),
                            dbc.Input(id={'type': "modal-card-name", 'index': card_id}, value=card_data['name'], className='card_board', type="text"),
                            html.H4('Description'),
                            dbc.Textarea(id={'type': "modal-card-desc", 'index': card_id}, value=card_data['desc'], className='card_board'),
                            html.H4('Due'),
                            dbc.Row([
                                dbc.Col(width={"size": 'auto'}, children=[
                                    dcc.DatePickerRange(
                                        id={'type': 'modal-card-date-picker-range', 'index': card_id}, className='card_board',
                                        display_format='Y/M/D', month_format='Y/M',
                                        initial_visible_month=now, start_date=start, end_date=due,
                                    ),
                                ]),
                                dbc.Col(width={"size": 'auto'}, children=[
                                    dbc.Button("x", id={'type': "button-delete-due-modal-card", 'index': card_id}, outline=True, color="warning", n_clicks=0, className='card_board'),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col(width={"size": 4}, children=[
                                    dmc.TimeInput(id={'type': 'time-input-start-modal-card', 'index': card_id}, value=start, class_name='card_board')
                                ]),
                                dbc.Col(width={"size": 4}, children=[
                                    dmc.TimeInput(id={'type': 'time-input-due-modal-card', 'index': card_id}, value=due, class_name='card_board')
                                ]),
                            ]),
                            dbc.Button('Confirm', id={'type': "button-confirm-modal-card", 'index': card_id}, color="warning", n_clicks=0)
                        ])
                    ])
                )
            cards.append(
                dbc.Button("+ Card", id={'type': "button-add-card", 'index': list_id}, outline=True, color="warning", className='button_add_card', n_clicks=0)
            )
            lists.append(
                html.Div(id={'type': "list", 'index': list_id}, className='list', children=[
                    dbc.Row(justify="between", children=[
                        dbc.Col(width={"size": 'auto'}, children=[
                            html.H4(list_data['name']),
                        ]),
                        dbc.Col(width={'size': 3, "order": "last"}, children=[
                            dbc.ButtonGroup(size="sm", children=[
                                dbc.Button("<", id={'type': "button-list-to-left", 'index': list_id}, outline=True, color="warning", n_clicks=0),
                                dbc.Button(">", id={'type': "button-list-to-right", 'index': list_id}, outline=True, color="warning", n_clicks=0)
                            ])
                        ])
                    ]),
                    dbc.Col(id={'type': "cards", 'index': list_id}, children=cards)
                ])
            )
            all_modals.append(
                html.Div(id={'type': 'modals', 'index': list_id}, children=modals),
            )
        PREV_N_LIST_TO_LEFT, PREV_N_LIST_TO_RIGHT = [None] * len(lists), [None] * len(lists)
        lists.append(
            html.Div(className='button_add_list', children=[
                dbc.Button("+ List", id="button-add-list", color="warning", className='button_add_list', n_clicks=0)
            ])
        )

        page_style = {'width': f'{60 + 179 + (len(lists) - 1) * 309}px'}

        return html.Div(id='page', style=page_style, className='page', children=[
            html.H3(BOARD_DATA['name'], id='board-name'),
            html.Div(id='board', children=[
                dbc.Row(id='lists', children=lists)
            ]),
            dbc.Modal(id="modal-add-list", is_open=False, children=[
                dbc.ModalBody([
                    dbc.ModalTitle("Input list name."),
                    dbc.Input(id="input-list-name", className='card_board', type="text"),
                    dbc.Button('Confirm', id="button-confirm-add-list", color="warning", n_clicks=0)
                ])
            ]),
            html.Div(id='all_modals', children=all_modals),
        ])


@dash.callback(
    Output("modal-add-list", "is_open"),
    [Input("button-add-list", "n_clicks"), Input("button-confirm-add-list", "n_clicks")],
    [State("modal-add-list", "is_open")],
    prevent_initial_call=True
)
def add_list_toggle_modal(n1, n2, is_open):
    global PREV_N1
    global PREV_N2
    if (n1 > PREV_N1) or (n2 > PREV_N2):
        is_open = not is_open
    PREV_N1, PREV_N2 = n1, n2
    return is_open


@dash.callback(
    [Output({'type': "modal-card", 'index': MATCH}, "is_open"),
     Output({'type': "card", 'index': MATCH}, "children"),
     Output({'type': "card", 'index': MATCH}, 'color'),
     Output({'type': 'modal-card-date-picker-range', 'index': MATCH}, 'start_date'),
     Output({'type': 'modal-card-date-picker-range', 'index': MATCH}, 'end_date'),
     Output({'type': 'time-input-start-modal-card', 'index': MATCH}, 'value'),
     Output({'type': 'time-input-due-modal-card', 'index': MATCH}, 'value')],
    [Input({'type': "button-card-open-modal", 'index': MATCH}, "n_clicks"),
     Input({'type': "button-confirm-modal-card", 'index': MATCH}, "n_clicks"),
     Input({'type': "button-delete-due-modal-card", 'index': MATCH}, 'n_clicks'),
     Input({'type': "modal-card-name", 'index': MATCH}, 'value'),
     Input({'type': "modal-card-desc", 'index': MATCH}, 'value')],
    [State({'type': "modal-card", 'index': MATCH}, "is_open"),
     State({'type': "modal-card", 'index': MATCH}, "id"),
     State({'type': "card", 'index': MATCH}, "children"),
     State({'type': "card", 'index': MATCH}, 'color'),
     State({'type': 'modal-card-date-picker-range', 'index': MATCH}, 'start_date'),
     State({'type': 'modal-card-date-picker-range', 'index': MATCH}, 'end_date'),
     State({'type': 'time-input-start-modal-card', 'index': MATCH}, 'value'),
     State({'type': 'time-input-due-modal-card', 'index': MATCH}, 'value')],
    prevent_initial_call=True
)
def card_toggle_modal(n1, n2, n3, name, desc, is_open, card_id_dict, card_children, color, start_date, due_date, start_time, due_time):
    global PREV_N1_CARD
    global PREV_N2_CARD
    global PREV_N3_CARD

    card_id = card_id_dict['index']

    if (n1 and card_id not in PREV_N1_CARD) or (card_id in PREV_N1_CARD and n1 > PREV_N1_CARD[card_id]):
        is_open = not is_open

    elif (n2 and card_id not in PREV_N2_CARD) or (card_id in PREV_N2_CARD and n2 > PREV_N2_CARD[card_id]):
        is_open = not is_open

        now = datetime.now(timezone.utc).astimezone()
        start, start_string = None, None
        if start_date is not None:
            start_date = datetime.fromisoformat(start_date).astimezone()
            start = start_date
            if start_time is not None:
                start_time = datetime.fromisoformat(start_time).astimezone()
                start = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=start_time.hour, minute=start_time.minute, second=start_time.second, tzinfo=start_time.tzinfo)
            start_string = start.isoformat()
        due, due_string = None, None
        if due_date is not None:
            due_date = datetime.fromisoformat(due_date).astimezone()
            due = due_date
            if due_time is not None:
                due_time = datetime.fromisoformat(due_time).astimezone()
                due = datetime(year=due_date.year, month=due_date.month, day=due_date.day, hour=due_time.hour, minute=due_time.minute, second=due_time.second, tzinfo=due_time.tzinfo)
            due_string = due.isoformat()

        color = None
        if due is not None:
            if now >= due:
                color = 'danger'
            elif timedelta(days=0) <= due - now <= timedelta(days=1):
                color = 'warning'

        BOARD_DATA['card_data'][card_id]['name'] = name
        BOARD_DATA['card_data'][card_id]['desc'] = desc
        BOARD_DATA['card_data'][card_id]['start'] = start_string
        BOARD_DATA['card_data'][card_id]['due'] = due_string

        card_children = [
            dbc.Row(justify="between", children=[
                dbc.Col(width={"size": 'auto'}, children=[
                    dbc.CardBody(name),
                ]),
                dbc.Col(width={"size": 'auto'}, children=[
                    dbc.Button("=", id={'type': "button-card-open-modal", 'index': card_id}, size="sm", color=None, n_clicks=0),
                ]),
            ])
        ]

    elif (n3 and card_id not in PREV_N3_CARD) or (card_id in PREV_N3_CARD and n3 > PREV_N3_CARD[card_id]):
        start_date, due_date, start_time, due_time = None, None, None, None

    PREV_N1_CARD[card_id], PREV_N2_CARD[card_id], PREV_N3_CARD[card_id] = n1, n2, n3

    with open(DATA_DIR/f'{BOARD_DATA["name"]}.json', 'w', encoding='utf-8') as f:
        json.dump(BOARD_DATA, f, ensure_ascii=False, indent=4)

    return is_open, card_children, color, start_date, due_date, start_time, due_time


@dash.callback(
    [Output('lists', 'children'), Output('input-list-name', 'value'), Output('page', 'style'), Output('all_modals', 'children')],
    [Input('button-confirm-add-list', 'n_clicks'), Input({'type': 'button-list-to-left', 'index': ALL}, 'n_clicks'), Input({'type': 'button-list-to-right', 'index': ALL}, 'n_clicks')],
    [State('lists', 'children'), State('input-list-name', 'value'), State('all_modals', 'children')],
    prevent_initial_call=True
)
def add_list(n_add_list, n_to_left, n_to_right, lists, list_name, all_modals):
    global PREV_N_ADD_LIST
    global PREV_N_LIST_TO_LEFT
    global PREV_N_LIST_TO_RIGHT

    left_index, right_index = None, None
    for index in range(len(n_to_left)):
        if n_to_left[index]:
            if PREV_N_LIST_TO_LEFT[index] is None or n_to_left[index] > PREV_N_LIST_TO_LEFT[index]:
                left_index = index
        if n_to_right[index]:
            if PREV_N_LIST_TO_RIGHT[index] is None or n_to_right[index] > PREV_N_LIST_TO_RIGHT[index]:
                right_index = index

    if n_add_list > PREV_N_ADD_LIST:
        new_list_id = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(24)])
        new_list = html.Div(id={'type': "list", 'index': new_list_id}, className='list', children=[
            dbc.Row(justify="between", children=[
                dbc.Col(width={"size": 'auto'}, children=[
                    html.H4(list_name),
                ]),
                dbc.Col(width={'size': 3, "order": "last"}, children=[
                    dbc.ButtonGroup(size="sm", children=[
                        dbc.Button("<", id={'type': "button-list-to-left", 'index': new_list_id}, outline=True, color="warning", n_clicks=0),
                        dbc.Button(">", id={'type': "button-list-to-right", 'index': new_list_id}, outline=True, color="warning", n_clicks=0)
                    ])
                ])
            ]),
            dbc.Col(id={'type': "cards", 'index': new_list_id}, children=[
                dbc.Button("+ Card", id={'type': "button-add-card", 'index': new_list_id}, outline=True, color="warning", className='button_add_card', n_clicks=0)
            ])
        ])
        lists.insert(-1, new_list)
        all_modals.append(
            html.Div(id={'type': 'modals', 'index': new_list_id}, children=[])
        )
        n_to_left.append(None)
        n_to_right.append(None)
        
        BOARD_DATA['list_data'][new_list_id] = {
            'name': list_name
        }
        BOARD_DATA['list'].append(new_list_id)
        BOARD_DATA['card'][new_list_id] = []
        PREV_N_ADD_LIST = n_add_list

    elif left_index is not None:
        if left_index > 0:
            BOARD_DATA['list'][left_index - 1], BOARD_DATA['list'][left_index] = BOARD_DATA['list'][left_index], BOARD_DATA['list'][left_index - 1]
            lists[left_index - 1], lists[left_index] = lists[left_index], lists[left_index - 1]
            n_to_left[left_index - 1], n_to_left[left_index] = n_to_left[left_index], n_to_left[left_index - 1]
            n_to_right[left_index - 1], n_to_right[left_index] = n_to_right[left_index], n_to_right[left_index - 1]
    
    elif right_index is not None:
        if right_index < len(BOARD_DATA['list']) - 1:
            BOARD_DATA['list'][right_index], BOARD_DATA['list'][right_index + 1] = BOARD_DATA['list'][right_index + 1], BOARD_DATA['list'][right_index]
            lists[right_index], lists[right_index + 1] = lists[right_index + 1], lists[right_index]
            n_to_left[right_index], n_to_left[right_index + 1] = n_to_left[right_index + 1], n_to_left[right_index]
            n_to_right[right_index], n_to_right[right_index + 1] = n_to_right[right_index + 1], n_to_right[right_index]
    
    page_style = {'width': f'{60 + 179 + (len(lists) - 1) * 309}px'}
    PREV_N_LIST_TO_LEFT, PREV_N_LIST_TO_RIGHT = n_to_left, n_to_right
    with open(DATA_DIR/f'{BOARD_DATA["name"]}.json', 'w', encoding='utf-8') as f:
        json.dump(BOARD_DATA, f, ensure_ascii=False, indent=4)
    
    return lists, '', page_style, all_modals
    

@dash.callback(
    [Output({'type': "cards", 'index': MATCH}, 'children'), Output({'type': 'modals', 'index': MATCH}, 'children')],
    [Input({'type': "button-add-card", 'index': MATCH}, 'n_clicks')],
    [State({'type': "cards", 'index': MATCH}, 'children'), State({'type': "cards", 'index': MATCH}, 'id'), State({'type': 'modals', 'index': MATCH}, 'children')],
    prevent_initial_call=True
)
def add_card(n_add_card, cards, list_id_dict, modals):
    global PREV_N_ADD_CARD
    global PREV_N_CARD_TO_LEFT
    global PREV_N_CARD_TO_RIGHT

    list_id = list_id_dict['index']

    if (n_add_card and list_id not in PREV_N_ADD_CARD) or (list_id in PREV_N_ADD_CARD and n_add_card > PREV_N_ADD_CARD[list_id]):
        now = datetime.now(timezone.utc).astimezone()

        new_card_id = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(24)])
        new_card = dbc.Card(id={'type': "card", 'index': new_card_id}, className='card', children=[
            dbc.Row(justify="between", children=[
                dbc.Col(width={"size": 'auto'}, children=[
                    dbc.CardBody('new card'),
                ]),
                dbc.Col(width={"size": 'auto'}, children=[
                    dbc.Button("=", id={'type': "button-card-open-modal", 'index': new_card_id}, size="sm", color=None, n_clicks=0),
                ]),
            ])
        ])
        cards.insert(-1, new_card)

        modals.append(
            dbc.Modal(id={'type': "modal-card", 'index': new_card_id}, is_open=False, children=[
                dbc.ModalBody([
                    html.H4('Name'),
                    dbc.Input(id={'type': "modal-card-name", 'index': new_card_id}, value='new card', className='card_board', type="text"),
                    html.H4('Description'),
                    dbc.Textarea(id={'type': "modal-card-desc", 'index': new_card_id}, value='', className='card_board'),
                    html.H4('Due'),
                    dbc.Row([
                        dbc.Col(width={"size": 'auto'}, children=[
                            dcc.DatePickerRange(
                                id={'type': 'modal-card-date-picker-range', 'index': new_card_id}, className='card_board',
                                display_format='Y/M/D', month_format='Y/M',
                                initial_visible_month=now, start_date=None, end_date=None,
                            ),
                        ]),
                        dbc.Col(width={"size": 'auto'}, children=[
                            dbc.Button("x", id={'type': "button-delete-due-modal-card", 'index': new_card_id}, outline=True, color="warning", n_clicks=0, className='card_board'),
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Col(width={"size": 4}, children=[
                            dmc.TimeInput(id={'type': 'time-input-start-modal-card', 'index': new_card_id}, value=None, class_name='card_board')
                        ]),
                        dbc.Col(width={"size": 4}, children=[
                            dmc.TimeInput(id={'type': 'time-input-due-modal-card', 'index': new_card_id}, value=None, class_name='card_board')
                        ]),
                    ]),
                    dbc.Button('Confirm', id={'type': "button-confirm-modal-card", 'index': new_card_id}, color="warning", n_clicks=0)
                ])
            ])
        )

        BOARD_DATA['card_data'][new_card_id] = {
            'list': BOARD_DATA['list_data'][list_id]['name'],
            'name': 'new card',
            'desc': '',
            'start': None,
            'due': None,
            'entries': [],
        }
        BOARD_DATA['card'][list_id].append(new_card_id)
        PREV_N_ADD_CARD[list_id] = n_add_card
        
    with open(DATA_DIR/f'{BOARD_DATA["name"]}.json', 'w', encoding='utf-8') as f:
        json.dump(BOARD_DATA, f, ensure_ascii=False, indent=4)

    return cards, modals
