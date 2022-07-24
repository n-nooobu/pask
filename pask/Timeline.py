import os
from pathlib import Path
import json
from datetime import datetime, date, timezone, timedelta
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/timeline')


DATA_DIR = Path(f'{os.path.dirname(__file__)}/data')


def layout():
    now = datetime.now(timezone.utc).astimezone()

    return html.Div(id='timeline-page', className='page', children=[
        dbc.Col([
            dcc.DatePickerRange(
                id='timeline-date-picker-range',
                display_format='Y/M/D', month_format='Y/M',
                initial_visible_month=now, start_date=now.date(), end_date=now.date(),
            ),
            dbc.Row(id='timelines'),
        ])
    ])


@dash.callback(
    [Output('timelines', 'children'), Output('timeline-page', 'style')],
    [Input('timeline-date-picker-range', 'start_date'), Input('timeline-date-picker-range', 'end_date')]
)
def show_timeline(start_date, end_date):
    start_date = datetime.fromisoformat(start_date).astimezone()
    end_date = datetime.fromisoformat(end_date).astimezone()

    cursor_date = start_date
    date_list = []
    while cursor_date <= end_date:
        date_list.append(cursor_date)
        cursor_date += timedelta(days=1)

    timelines = []
    for date in date_list:
        entries = []
        category_sum = {}
        for json_path in DATA_DIR.glob('*.json'):
            if json_path.stem == 'category':
                continue
            with open(json_path, 'r', encoding='utf-8') as f:
                board_data = json.load(f)
            
            for list_id in board_data['list']:
                list_data = board_data['list_data'][list_id]
                for card_id in board_data['card'][list_id]:
                    card_data = board_data['card_data'][card_id]
                    for entry_id in board_data['entry'][card_id]:
                        entry_data = board_data['entry_data'][entry_id]
                        if entry_data['start'] is None or entry_data['end'] is None:
                            continue
                        start = datetime.fromisoformat(entry_data['start']).astimezone()
                        if date <= start < date + timedelta(days=1):
                            entry = {
                                'list_id': list_id,
                                'list_name': list_data['name'],
                                'card_id': card_id,
                                'card_name': card_data['name'],
                                'category': card_data['category'],
                                'entry_id': entry_id,
                                'entry_desc': entry_data['desc'],
                                'entry_start': datetime.fromisoformat(entry_data['start']).astimezone(),
                                'entry_end': datetime.fromisoformat(entry_data['end']).astimezone(),
                            }
                            entry['entry_delta'] = entry['entry_end'] - entry['entry_start']
                            if entry['category'] not in category_sum:
                                category_sum[entry['category']] = entry['entry_delta']
                            else:
                                category_sum[entry['category']] += entry['entry_delta']
                            entries.append(entry)
        entries = sorted(entries, key=lambda x: x['entry_start'])

        working_hours = []
        for category, delta in category_sum.items():
            working_hours.append(f"{category}: {str(delta)[:-3]}")
            working_hours.append(html.Br())
        timeline = [html.H3(date.date().isoformat())]
        timeline.append(
            dbc.Card(className='timeline_card', children=[
                html.H4('Working hours'),
                html.P(working_hours),
            ])
        )
        for entry in entries:
            timeline.append(
                dbc.Card(className='timeline_card', children=[
                    html.H4(f"{entry['entry_start'].strftime('%H:%M')} - {entry['entry_end'].strftime('%H:%M')}"),
                    html.P([
                        f"Card: {entry['card_name']}", html.Br(),
                        f"Category: {entry['category']}", html.Br(),
                        f"Description: {entry['entry_desc'] if len(entry['entry_desc']) < 40 else entry['entry_desc'][:40] + '...'}",
                    ]),
                ])
            )

        timelines.append(
            html.Div(className='timeline', children=timeline)
        )

    page_style = {'width': f'{60 + (len(date_list)) * 559}px'}

    return timelines, page_style
