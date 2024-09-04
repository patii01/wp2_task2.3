#Imports

import json
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash
import dash_daq as daq
from math import ceil
from dateutil import parser
import random
from PIL import Image


STATUS = Image.open("images/status.png")
SATELLITE = Image.open("images/satellite.png")
CONJUCTIONS = Image.open("images/conjuctions.png")
MANOEUVRES = Image.open("images/manoeuvres.png")
FILES = Image.open("images/files.png")
CHAT = Image.open("images/chat.png")
OPERATOR = Image.open("images/operator.png")

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#Use Case 2 - Position
#Data
# Load the data
with open('UseCase2_data/data_test.json') as f:
    dataSets_position = json.load(f)

target_values = list({dataSets_position[key]['target'] for key in dataSets_position})
chaser_values = list({dataSets_position[key]['chaser'] for key in dataSets_position})

dates = []
for key in dataSets_position:
    for dt_str in dataSets_position[key]['dt_time']:
        dates.append(datetime.fromisoformat(dt_str).date())

with open('UseCase2_data/neuraspace_test.json') as f:
    Neuraspace_position = json.load(f)
Neuraspace_position["tca"] = dataSets_position[list(dataSets_position.keys())[0]]['tca'], 

with open('UseCase1_data/data_test.json') as f:
    dataSets_forecast = json.load(f)

target_chaser_values = list({dataSets_forecast[key]['name'] for key in dataSets_forecast})
target_chaser_values.append('Neuraspace')


now = parser.parse("2024-05-30 19:39:41.572 +0100")
dates.append("2024-05-30 19:39:41+00:00")
dates.append(Neuraspace_position["tca"])
dt_time = list(set(dates))

with open('UseCase1_data/neuraspace_test.json') as f:
    Neuraspace_forecast = json.load(f)


# Funtions
def hex_to_rgba(hex_color, opacity):
    hex_color = hex_color.strip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'

def hexToRgb(hex):
    # Remove o '#' inicial, se presente
    hex = hex.lstrip('#')
    
    # Converte a string hexadecimal em componentes RGB separadas
    bigint = int(hex, 16)
    r = (bigint >> 16) & 255
    g = (bigint >> 8) & 255
    b = bigint & 255
    
    return {'r': r, 'g': g, 'b': b}

def rgbToHex(r, g, b):
    # Converte cada componente RGB em sua representação hexadecimal
    return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)                   

def get_max_min_UC2(dataSets, flag):
    daily_data = {}
    keys = len(dataSets.keys())
    if keys > 5:
        keys = 5
    for dataSet in dataSets.values():
        for idx, time in enumerate(dataSet['dt_time']):
            date_str = datetime.fromisoformat(time).date()  # Extract the date part
            if date_str not in daily_data:
                daily_data[date_str] = []

            if flag == 1:
                data = dataSet['dt']['MissDistance'][idx]
            elif flag == 2:
                data = dataSet['dt']['Radial'][idx]
            elif flag == 3:
                data = dataSet['dt']['AlongTrack'][idx]
            else:
                data = dataSet['dt']['CrossTrack'][idx]
            
            daily_data[date_str].append({data: time})

    daily_data = dict(sorted(daily_data.items()))
    for date, values in daily_data.items():
        daily_data[date] = sorted(values, key=lambda x: list(x.values())[0])
    
    dt_time_min = []
    dt_time_max = []
    min_values = []
    max_values = []

    for date, values in daily_data.items():
        all_data_at_date = [list(d.keys())[0] for d in values]  # Extracting data values
        all_times_at_date = [list(d.values())[0] for d in values]  # Extracting corresponding times

        if len(all_data_at_date) > 2:
            for i in range(0, len(all_data_at_date), keys):
                subset_data = all_data_at_date[i:i+keys]
                subset_times = all_times_at_date[i:i+keys]

                min_val = min(subset_data)
                max_val = max(subset_data)
                min_values.append(min_val)
                max_values.append(max_val)

                dt_time_min.append(subset_times[subset_data.index(min_val)])
                dt_time_max.append(subset_times[subset_data.index(max_val)])
        else:
            min_val = min(all_data_at_date)
            max_val = max(all_data_at_date)
            min_values.append(min_val)
            max_values.append(max_val)
            
            dt_time_min.append(all_times_at_date[all_data_at_date.index(min_val)])
            dt_time_max.append(all_times_at_date[all_data_at_date.index(max_val)])

    return dt_time_min, min_values, dt_time_max, max_values

forecast_begin_chaser = {}
forecast_begin_target = {}

def find_closest_before(target_time, times):
    target_dt = datetime.fromisoformat(target_time)
    closest_time = None
    for time in times:
        dt = datetime.fromisoformat(time)
        if dt <= target_dt:
            if closest_time is None or dt > datetime.fromisoformat(closest_time):
                closest_time = time
    return closest_time

def init_forecast_begin(type, forecast_begin):
    dataSets_for_forecast = dataSets_forecast.copy()
    dataSets_for_forecast['Neuraspace'] = Neuraspace_forecast
    for dataset in dataSets_for_forecast:
        forecast_begin[dataset] = {}
        if dataset != 'Neuraspace':
            dt = dataSets_for_forecast[dataset]['Forecast'][type]
            times = dataSets_for_forecast[dataset][type]['dt_time']
        else:
            dt = dataSets_for_forecast[dataset]['Forecast']
            times = dataSets_for_forecast[dataset]['dt_time']
        for model_name, model_forecast in dt.items():
            if model_forecast['dt_time'] != []:
                first_model_time = model_forecast['dt_time'][0]
                closest_time_before = find_closest_before(first_model_time, times)
                if closest_time_before != None:
                    if closest_time_before not in forecast_begin[dataset]:
                        forecast_begin[dataset][closest_time_before] = {}
                    forecast_begin[dataset][closest_time_before][model_name] = {
                        'name': closest_time_before,
                        'dt_time': model_forecast['dt_time'],
                        'AlongTrack': {
                            'dt': model_forecast['AlongTrack']['dt'],
                            'upper_bound': model_forecast['AlongTrack']['upper_bound'],
                            'lower_bound': model_forecast['AlongTrack']['lower_bound'],
                            'color': model_forecast['AlongTrack']['color']
                        },
                        'CrossTrack': {
                            'dt': model_forecast['CrossTrack']['dt'],
                            'upper_bound': model_forecast['CrossTrack']['upper_bound'],
                            'lower_bound': model_forecast['CrossTrack']['lower_bound'],
                            'color': model_forecast['CrossTrack']['color']
                        },
                        'Radial': {
                            'dt': model_forecast['Radial']['dt'],
                            'upper_bound': model_forecast['Radial']['upper_bound'],
                            'lower_bound': model_forecast['Radial']['lower_bound'],
                            'color': model_forecast['Radial']['color']
                        }
                    }
    return forecast_begin
             
def get_max_min_forecast(dataSets, flag, type):
    daily_data = {}
    count = 0
    keys = len(dataSets.keys())
    if keys > 5:
        keys = 5

    for dataSet in dataSets.values():
        count += 1
        for idx, time in enumerate(dataSet[type]['dt_time']):
            date_str = datetime.fromisoformat(time).date()  # Extract the date part
            data = 0
            if date_str not in daily_data:
                daily_data[date_str] = []
            
            if flag == 1:
                data = dataSet[type]['Radial']['dt'][idx]
            elif flag == 2:
                data = dataSet[type]['AlongTrack']['dt'][idx]
            else:
                data = dataSet[type]['CrossTrack']['dt'][idx]
            
            daily_data[date_str].append({data: time})

    daily_data = dict(sorted(daily_data.items()))
    for date, values in daily_data.items():
        daily_data[date] = sorted(values, key=lambda x: list(x.values())[0])
    
    dt_time_min = []
    dt_time_max = []
    min_values = []
    max_values = []

    for date, values in daily_data.items():
        all_data_at_date = [list(d.keys())[0] for d in values]  # Extracting data values
        all_times_at_date = [list(d.values())[0] for d in values]  # Extracting corresponding times

        if len(all_data_at_date) > 2:
            for i in range(0, len(all_data_at_date), keys):
                subset_data = all_data_at_date[i:i+keys]
                subset_times = all_times_at_date[i:i+keys]

                min_val = min(subset_data)
                max_val = max(subset_data)
                min_values.append(min_val)
                max_values.append(max_val)

                dt_time_min.append(subset_times[subset_data.index(min_val)])
                dt_time_max.append(subset_times[subset_data.index(max_val)])
        else:
            min_val = min(all_data_at_date)
            max_val = max(all_data_at_date)
            min_values.append(min_val)
            max_values.append(max_val)
            
            dt_time_min.append(all_times_at_date[all_data_at_date.index(min_val)])
            dt_time_max.append(all_times_at_date[all_data_at_date.index(max_val)])

    return dt_time_min, min_values, dt_time_max, max_values

existing_colors = [dataSets_forecast[key]['color'] for key in dataSets_forecast] + ["#000031"]
def generate_random_color(existing_colors):
    while True:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        if color not in existing_colors:
            existing_colors.append(color)
            return color

def getcolor():
    for d in dataSets_forecast.keys():
        for key, value in dataSets_forecast[d]['Forecast']['Target'].items():
            value['AlongTrack']['color'] = generate_random_color(existing_colors)
            value['CrossTrack']['color'] = generate_random_color(existing_colors)
            value['Radial']['color'] = generate_random_color(existing_colors)

        for key, value in dataSets_forecast[d]['Forecast']['Chaser'].items():
            value['AlongTrack']['color'] = generate_random_color(existing_colors)
            value['CrossTrack']['color'] = generate_random_color(existing_colors)
            value['Radial']['color'] = generate_random_color(existing_colors)
    for key, value in Neuraspace_forecast['Forecast'].items():
        value['AlongTrack']['color'] = generate_random_color(existing_colors)
        value['CrossTrack']['color'] = generate_random_color(existing_colors)
        value['Radial']['color'] = generate_random_color(existing_colors)
    
    return dataSets_forecast

# Layout
sidebar = dbc.Nav(
    [
        html.Img(src=STATUS, className="img_sidebar"),
        html.Img(src=SATELLITE, className="img_sidebar"),
        html.Img(src=CONJUCTIONS, className="img_sidebar"),
        html.Img(src=MANOEUVRES, className="img_sidebar"),
        html.Img(src=FILES, className="img_sidebar"),
        html.Img(src=CHAT, className="img_sidebar"),
        html.Img(src=OPERATOR, className="img_sidebar")
    ],
    id="sidebar",
    className="sidebar-fixed",
    vertical=True,
)

title_PositionCase = html.Div([
    html.Div([
        html.H6("Position"),
        dbc.Button( "i",
            id="hover-target",
            className="circle-button me-1",
            n_clicks=0,
        ),
        dbc.Popover(
            [
                dbc.PopoverHeader("Information"),
                dbc.PopoverBody("Grey Area: Link between the maximum and minimum position values for each time interval."),
            ],
            target="hover-target",
            body=True,
            trigger="hover",
            className="popover-box",
        ),
    ], className='info-button'),
])

eixos_PositionCase = html.Div([
    html.Button('Miss Distance', id='btn-1', n_clicks=0, className='eixos-button active'),
    html.Button('Radial', id='btn-2', n_clicks=0, className='eixos-button'),
    html.Button('Along-track', id='btn-3', n_clicks=0, className='eixos-button'),
    html.Button('Cross-track', id='btn-4', n_clicks=0, className='eixos-button')
], className='eixos-container')

position_graph = html.Div([
    html.Div([
        html.Div([
            html.Label('Switch between single and'),
            html.Label('multiple series selection'),
        ], className='switch-label'),
        daq.BooleanSwitch(
            id='boolean-switch',
            on=False,
            color="#701FBE",
        ),
    ], className='switch-container'),
    
    html.Div(id='selection-series-content', children=[
        html.Div([
            dcc.Dropdown(
                id='chaser',
                options=[{'label': i, 'value': i} for i in chaser_values],
                placeholder="Source Chaser"
            )
        ], className='dropdown-container'),
        html.Div([
            dcc.Dropdown(
                id='target',
                options=[{'label': i, 'value': i} for i in target_values],
                placeholder="Source Target"
            )
        ], className='dropdown-container'),
        html.Div([
            dcc.Graph(id='position_graph'),
        ], className='graph'),
    ]),
    
    html.Div(id='compare-series-content', style={'display': 'none'}, children=[
        html.Div([
            dcc.Dropdown(
                id='series',
                options=[{'label': key, 'value': key} for key in dataSets_position.keys()],
                placeholder="Select Series",
                multi=True
            )
        ], className='dropdown-container'),
        html.Div([
            dcc.Graph(id='multiple_graph'),
        ], className='graph'),
    ]),
    
    html.Div([
        dcc.Graph(id='update_multiple')
    ], className='graph_multiple'),
], style={'display': 'flex'})

title_ForecastChaser = html.Div([
    html.Div([
        html.H6("Chaser Position Uncertainty", className='title-forecast'),
        dbc.Button( "i",
            id="hover-target2",
            className="circle-button me-1",
            n_clicks=0,
        ),
        dbc.Popover(
            [
                dbc.PopoverHeader("Information"),
                dbc.PopoverBody("Grey Area: Link between the maximum and minimum position values for each time interval."),
                dbc.PopoverBody("Use Shift to select multiple forecasts."),
            ],
            target="hover-target2",
            body=True,
            trigger="hover",
            className="popover-box",
        ),
    ], className='info-button'),
])

eixos_ForecastChaser = html.Div([
    html.Button('Radial', id='btn-5', n_clicks=0, className='tab-button'),
    html.Button('Along-track', id='btn-6', n_clicks=0, className='tab-button'),
    html.Button('Cross-track', id='btn-7', n_clicks=0, className='tab-button')
], className='eixos')

forecast_chaser_graph = html.Div([
     html.Div([
        html.Div([
            html.Label('Switch between single and'),
            html.Label('multiple series selection'),
        ], className='switch-label'),
        daq.BooleanSwitch(
            id='boolean-switch2',
            on=False,
            color="#701FBE",
        ),
    ], className='switch-container'),
    html.Div(id='series-content2', children=[
        html.Div([
            dcc.Dropdown(
                id='selection_series',
                options=[{'label': i, 'value': i} for i in target_chaser_values],
                placeholder="Selection of chaser"
            )
        ], className='dropdown-container_f'),
        html.Div([
            dcc.Graph(id='forecast_chaser_graph')
        ], className='graph')
    ]),
    html.Div(id='compare-content2', children=[
        html.Div([
            dcc.Dropdown(
                id='compare_series',
                options=[{'label': i, 'value': i} for i in target_chaser_values],
                placeholder="Selection of series",
                multi=True
            )
        ], className='dropdown-container_f'),
        html.Div([
            dcc.Graph(id='multiple_chaser_graph')
        ], className='graph')
    ], style={'display': 'none'})
 ])   

title_ForecastTarget = html.Div([
    html.Div([
        html.H6("Target Position Uncertainty", className='title-forecast'),
        dbc.Button( "i",
            id="hover-target3",
            className="circle-button me-1",
            n_clicks=0,
        ),
        dbc.Popover(
            [
                dbc.PopoverHeader("Information"),
                dbc.PopoverBody("Grey Area: Link between the maximum and minimum position values for each time interval."),
                dbc.PopoverBody("Use Shift to select multiple forecasts."),
            ],
            target="hover-target3",
            body=True,
            trigger="hover",
            className="popover-box",
        ),
    ], className='info-button'),
])

eixos_ForecastTarget = html.Div([
    html.Button('Radial', id='btn-8', n_clicks=0, className='tab-button'),
    html.Button('Along-track', id='btn-9', n_clicks=0, className='tab-button'),
    html.Button('Cross-track', id='btn-10', n_clicks=0, className='tab-button')
], className='eixos')

forecast_target_graph = html.Div([
     html.Div([
        html.Div([
            html.Label('Switch between single and'),
            html.Label('multiple series selection'),
        ], className='switch-label'),
        daq.BooleanSwitch(
            id='boolean-switch3',
            on=False,
            color="#701FBE",
        ),
    ], className='switch-container'),
    html.Div(id='series-content3', children=[
        html.Div([
            dcc.Dropdown(
                id='selection_series1',
                options=[{'label': i, 'value': i} for i in target_chaser_values],
                placeholder="Selection of Target"
            )
        ], className='dropdown-container_f'),
        html.Div([
            dcc.Graph(id='forecast_target_graph')
        ], className='graph')
    ]),
    html.Div(id='compare-content3', children=[
        html.Div([
            dcc.Dropdown(
                id='compare_series1',
                options=[{'label': i, 'value': i} for i in target_chaser_values],
                placeholder="Selection of series",
                multi=True
            )
        ], className='dropdown-container_f'),
        html.Div([
            dcc.Graph(id='multiple_target_graph')
        ], className='graph')
    ], style={'display': 'none'})
 ])   

# Define the layout of the app
app.layout = html.Div([
    dbc.Offcanvas(
        [
            html.Div(className="sidebar-item", children=[
                html.Img(src=STATUS, className="img_sidebar"),
                html.P("Status", className="sidebar_title")
            ]),
            html.Div(className="sidebar-item", children=[
                html.Img(src=SATELLITE, className="img_sidebar"),
                html.P("Satellite", className="sidebar_title")
            ]),
            html.Div(className="sidebar-item", children=[
                html.Img(src=CONJUCTIONS, className="img_sidebar"),
                html.P("Conjunctions", className="sidebar_title")
            ]),
            html.Div(className="sidebar-item", children=[
                html.Img(src=MANOEUVRES, className="img_sidebar"),
                html.P("Manoeuvres", className="sidebar_title")
            ]),
            html.Div(className="sidebar-item", children=[
                html.Img(src=FILES, className="img_sidebar"),
                html.P("Files", className="sidebar_title")
            ]),
            html.Div(className="sidebar-item", children=[
                html.Img(src=CHAT, className="img_sidebar"),
                html.P("Chat", className="sidebar_title")
            ]),
            html.Div(className="sidebar-item", children=[
                html.Img(src=OPERATOR, className="img_sidebar"),
                html.P("Operator", className="sidebar_title")
            ]),
        ],
        id="offcanvas",
        is_open=False,
        className="offcanvas-custom",
        backdrop=False,
        close_button=False
    ),
    
    sidebar,
    
    # Content
    html.Div(id="content", className="content", children=[
        html.H1("Evolution"),
        html.Div([
            title_PositionCase,
            eixos_PositionCase
        ]),
        position_graph,

        dcc.Store(id='button_id', data='btn-1'),  # Store for button id
        dcc.Store(id='button_id2', data='btn-1'),  # Store for button id
        dcc.Store(id='button_m', data='btn-1'),  # Store for button id
        
        html.Div([
            title_ForecastChaser,
            eixos_ForecastChaser
        ]),
        forecast_chaser_graph,

        dcc.Store(id='button_id3', data='btn-5'),  # Store for button id
        dcc.Store(id='button_id4', data='btn-5'),  # Store for button id
        dcc.Store(id='selected-points', data=[]),  # Store for selected points
        dcc.Store(id='selected-points2', data=[]),  # Store for selected points  

        html.Div([
            title_ForecastTarget,
            eixos_ForecastTarget
        ]),
        forecast_target_graph,

        dcc.Store(id='button_id5', data='btn-8'),  # Store for button id
        dcc.Store(id='button_id6', data='btn-8'),  # Store for button id
        dcc.Store(id='selected-point3', data=[]),  # Store for selected points
        dcc.Store(id='selected-points4', data=[]),  # Store for selected points  

    ]),


    dbc.Navbar(
        dbc.Container([
            # Hamburger menu button
            html.Button(className="hamburger", id="hamburger-button", n_clicks=0, children=[
                html.Span(),
                html.Span(),
                html.Span()
            ]),  
            # Logo
            html.A(
                html.Img(src="https://app.stg.neuraspace.com/Dark-Horizontal-Logo.svg"),
                className="navbar-brand"
            ),
        ]),
        className="navbar-custom",
    ),
])


#Menu
@app.callback(
    [Output("offcanvas", "is_open"), Output("content", "className")],
    [Input("hamburger-button", "n_clicks")],
    [State("offcanvas", "is_open")]
)
def toggle_offcanvas(n_clicks, is_open):
    if n_clicks:
        new_is_open = not is_open
        new_class_name = "content shift-right" if new_is_open else "content"
        return new_is_open, new_class_name
    return is_open, "content"

#Button active
@app.callback(
    [Output('btn-1', 'className'),
     Output('btn-2', 'className'),
     Output('btn-3', 'className'),
     Output('btn-4', 'className')],
    [Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks'),
     Input('btn-4', 'n_clicks')]
)
def update_button_classes_position(btn1, btn2, btn3, btn4):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['eixos-button active', 'eixos-button', 'eixos-button', 'eixos-button']
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return [
            'eixos-button active' if button_id == 'btn-1' else 'eixos-button',
            'eixos-button active' if button_id == 'btn-2' else 'eixos-button',
            'eixos-button active' if button_id == 'btn-3' else 'eixos-button',
            'eixos-button active' if button_id == 'btn-4' else 'eixos-button'
        ]

@app.callback(
    [Output('btn-5', 'className'),
     Output('btn-6', 'className'),
     Output('btn-7', 'className')],
    [Input('btn-5', 'n_clicks'),
     Input('btn-6', 'n_clicks'),
     Input('btn-7', 'n_clicks')]
)
def update_button_classes_forecast1(btn1, btn2, btn3):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['tab-button active', 'tab-button', 'tab-button']
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return [
            'tab-button active' if button_id == 'btn-5' else 'tab-button',
            'tab-button active' if button_id == 'btn-6' else 'tab-button',
            'tab-button active' if button_id == 'btn-7' else 'tab-button',
        ]

@app.callback(
    [Output('btn-8', 'className'),
     Output('btn-9', 'className'),
     Output('btn-10', 'className')],
    [Input('btn-8', 'n_clicks'),
     Input('btn-9', 'n_clicks'),
     Input('btn-10', 'n_clicks')]
)
def update_button_classes_forecast2(btn1, btn2, btn3):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['tab-button active', 'tab-button', 'tab-button']
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return [
            'tab-button active' if button_id == 'btn-8' else 'tab-button',
            'tab-button active' if button_id == 'btn-9' else 'tab-button',
            'tab-button active' if button_id == 'btn-10' else 'tab-button',
        ]

#Switch
@app.callback(
    [Output('selection-series-content', 'style'),
     Output('compare-series-content', 'style')],
    [Input('boolean-switch', 'on')]
)
def toggle_content(switch_on):
    if switch_on:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'none'}
    
@app.callback(
    [Output('series-content2', 'style'),
     Output('compare-content2', 'style')],
    [Input('boolean-switch2', 'on')]
)
def toggle_content2(switch_on):
    if switch_on:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'none'}

@app.callback(
    [Output('series-content3', 'style'),
     Output('compare-content3', 'style')],
    [Input('boolean-switch3', 'on')]
)
def toggle_content3(switch_on):
    if switch_on:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'none'}


# Position Graph - Use Case 2
def plot_position1(fig, target, chaser, max_value, colorN, dt_time, flag):
    tca = parser.parse(dataSets_position[list(dataSets_position.keys())[0]]['tca'])
    min_value = 0
    
    if flag == 2:
        data = dataSets_position[target + ' vs ' + chaser]['dt']['Radial']
        upper = dataSets_position[target + ' vs ' + chaser]['upper_bound']['Radial']
        lower = dataSets_position[target + ' vs ' + chaser]['lower_bound']['Radial']
        upper_Neuraspace = Neuraspace_position['upper_bound']['Radial']
        lower_Neuraspace = Neuraspace_position['lower_bound']['Radial']
        warning = dataSets_position[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets_position[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace_position['dt']['Radial']
        max_value = max([max_value] + data + upper + upper_Neuraspace)
        min_value = min([0] + lower + lower_Neuraspace)
    elif flag == 3:
        data = dataSets_position[target + ' vs ' + chaser]['dt']['AlongTrack']
        upper = dataSets_position[target + ' vs ' + chaser]['upper_bound']['AlongTrack']
        lower = dataSets_position[target + ' vs ' + chaser]['lower_bound']['AlongTrack']
        upper_Neuraspace = Neuraspace_position['upper_bound']['AlongTrack']
        lower_Neuraspace = Neuraspace_position['lower_bound']['AlongTrack']
        warning = dataSets_position[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets_position[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace_position['dt']['AlongTrack']
        max_value = max([max_value] + data + upper + upper_Neuraspace)
        min_value = min([0] + lower + lower_Neuraspace)
    elif flag == 4:
        data = dataSets_position[target + ' vs ' + chaser]['dt']['CrossTrack']
        upper = dataSets_position[target + ' vs ' + chaser]['upper_bound']['CrossTrack']
        lower = dataSets_position[target + ' vs ' + chaser]['lower_bound']['CrossTrack']
        upper_Neuraspace = Neuraspace_position['upper_bound']['CrossTrack']
        lower_Neuraspace = Neuraspace_position['lower_bound']['CrossTrack']
        warning = dataSets_position[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets_position[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace_position['dt']['CrossTrack']
        max_value = max([max_value] + data + upper + upper_Neuraspace)
        min_value = min([0] + lower + lower_Neuraspace)

    else:
        data = dataSets_position[target + ' vs ' + chaser]['dt']['MissDistance']
        warning = dataSets_position[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets_position[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace_position['dt']['MissDistance']
        max_value = max([max_value] + data)
        min_value = min([min_value] + data)

    fig.add_trace(
        go.Scatter(
            x=dataSets_position[target + ' vs ' + chaser]['dt_time'], y=data, mode='lines', name=dataSets_position[target + ' vs ' + chaser]['name'], line=dict(color=dataSets_position[target + ' vs ' + chaser]['color'])
        )   
    )


    fig.add_trace(
        go.Scatter(
            x=dt_time, y=[warning] * len(dt_time), mode='lines', name='Warning Threshold', line=dict(color='#FFB000', dash='dash'), showlegend=True
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dt_time, y=[alert] * len(dt_time), mode='lines', name='Alert Threshold', line=dict(color='#EA3F6D', dash='dash'), showlegend=True
        )
    )
    

    if flag != 1:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'],
                y=upper_Neuraspace,  # Ignorar pontos com 0
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )

        # Adicionar a banda de erro inferior
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'],
                y=lower_Neuraspace,  
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  
                fillcolor=colorN,  
                showlegend=False
            )
        )

        # Adicionar a banda de erro superior
        fig.add_trace(
            go.Scatter(
                x=dataSets_position[target + ' vs ' + chaser]['dt_time'],
                y=upper,  # Ignorar pontos com 0
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )

        # Adicionar a banda de erro inferior
        fig.add_trace(
            go.Scatter(
                x=dataSets_position[target + ' vs ' + chaser]['dt_time'],
                y=lower,  
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  
                fillcolor=hex_to_rgba(dataSets_position[target + ' vs ' + chaser]['color'], 0.3),  
                showlegend=False
            )
        )

    if now > tca:
        fig.add_shape(
            type='rect', x0=tca, y0=min_value-100, x1=now, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
            showlegend=False
        )

    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'], y=neura, mode='lines', name=Neuraspace_position['name'], line=dict(color='#000031')
            )
    )
    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            )
        ]
    )

    fig.update_xaxes(gridcolor='#E5ECF6')

    fig.update_yaxes(gridcolor='#E5ECF6')

    fig.update_layout(plot_bgcolor='white', 
                      hovermode="x unified")
    
    fig.update_traces(
        hovertemplate='<br>'.join([
            '<br>'
            'Position: %{y}'
        ]),
    )

@app.callback(
    [Output('position_graph', 'figure'),
     Output('button_id', 'data')],
    [Input('target', 'value'),
     Input('chaser', 'value'),
     Input('button_id', 'data'),
     Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks'),
     Input('btn-4', 'n_clicks')]
)
def mainPlot_position(target, chaser, button_id, btn1, btn2, btn3, btn4):
    tca = parser.parse(dataSets_position[list(dataSets_position.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  
    fig = make_subplots()
    colorN = hex_to_rgba('#000031', 0.3)
    min_value = 0
    
    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 2)
        max_value = max(max_values + Neuraspace_position['dt']['Radial'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        min_value = min(min_values + Neuraspace_position['dt']['Radial'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        neura = Neuraspace_position['dt']['Radial']
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 3)
        max_value = max(max_values + Neuraspace_position['dt']['AlongTrack'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        min_value = min(min_values + Neuraspace_position['dt']['AlongTrack'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        neura = Neuraspace_position['dt']['AlongTrack']
    elif button_id == 'btn-4':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 4)
        max_value = max(max_values + Neuraspace_position['dt']['CrossTrack'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        min_value = min(min_values + Neuraspace_position['dt']['CrossTrack'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        neura = Neuraspace_position['dt']['CrossTrack']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 1)
        max_value = max(max_values + Neuraspace_position['dt']['MissDistance'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        min_value = min(min_values + Neuraspace_position['dt']['MissDistance'] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        neura = Neuraspace_position['dt']['MissDistance']

    
    if target is None or chaser is None:

        # lines with x=TCA and x=NOW
        fig.add_shape(
            type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
            name='TCA', showlegend=False
        )
        fig.add_shape(
            type='line', x0=now, y0=min_value-100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
            name='Now',showlegend=False
        )

        # Adding annotations above the TCA and Now lines
        fig.update_layout(
            annotations=[
                dict(
                    x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
                ),
                dict(
                    x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
                )
            ]
        )

        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'], y=neura, mode='lines', name=Neuraspace_position['name'], line=dict(color="#000031", width=2)
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_min, 
                y=min_values,
                line=dict(color='rgba(255,255,255,0)'), showlegend=False, hoverinfo='none')
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_max, 
                y=max_values, fill='tonexty',
                fillcolor='rgba(217,217,217, 0.5)', line=dict(color='rgba(217,217,217, 0.5)'), showlegend=False, hoverinfo='none')
        )
        
        for dataSet in dataSets_position:
            if button_id == 'btn-2':
                data = dataSets_position[dataSet]['dt']['Radial']
            elif button_id == 'btn-3':
                data = dataSets_position[dataSet]['dt']['AlongTrack']
            elif button_id == 'btn-4':
                data = dataSets_position[dataSet]['dt']['CrossTrack']
            else:
                data = dataSets_position[dataSet]['dt']['MissDistance']
            fig.add_trace(
                go.Scatter(
                    x=dataSets_position[dataSet]['dt_time'], y=data, mode='markers', name=dataSets_position[dataSet]['name'], marker=dict(color=dataSets_position[dataSet]['color']))
            )

        fig.update_traces(
            hovertemplate='<br>'.join([
                '<br>'
                'Position: %{y}'
         ]),
    )
    
    else:
        if target + ' vs ' + chaser not in dataSets_position:
            fig.add_annotation(
                xref='paper', yref='paper',
                x=0.5, y=0.5,
                text='No data available for the selected series.',
                showarrow=False,
                font=dict(size=20),
                align='center',
                bordercolor='#767689',
            )
        elif button_id == 'btn-2':
            plot_position1(fig, target, chaser, max_value, colorN, dt_time, 2)
        elif button_id == 'btn-3':
            plot_position1(fig, target, chaser, max_value, colorN, dt_time, 3)
        elif button_id == 'btn-4':
            plot_position1(fig, target, chaser, max_value, colorN, dt_time, 4)
        else:
            plot_position1(fig, target, chaser, max_value, colorN, dt_time, 1)


    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(
        plot_bgcolor='white',
        legend=dict(
            x=0,
            y=-1,  # Adjusted to ensure it stays just below the graph
            orientation='h',
            yanchor='bottom',  # Ensure this is consistent with 'y'
            xanchor='left',
            traceorder='normal',
            font=dict(size=10),
            itemwidth=30,
        ),
        margin=dict(l=50, r=20, t=40, b=10),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    return fig, button_id

def plot_position(fig, series, max_value, colorN, dt_time, flag):
    tca = parser.parse(dataSets_position[list(dataSets_position.keys())[0]]['tca'])
    warning = Neuraspace_position['Total']['warning']
    alert = Neuraspace_position['Total']['alert']
    min_value = 0
    
    if flag == 2:
        upper_Neuraspace = Neuraspace_position['upper_bound']['Radial']
        lower_Neuraspace = Neuraspace_position['lower_bound']['Radial']
        neura = Neuraspace_position['dt']['Radial']
    elif flag == 3:
        upper_Neuraspace = Neuraspace_position['upper_bound']['AlongTrack']
        lower_Neuraspace = Neuraspace_position['lower_bound']['AlongTrack']
        neura = Neuraspace_position['dt']['AlongTrack']
    elif flag == 4:
        upper_Neuraspace = Neuraspace_position['upper_bound']['CrossTrack']
        lower_Neuraspace = Neuraspace_position['lower_bound']['CrossTrack']
        neura = Neuraspace_position['dt']['CrossTrack']
    else:
        neura = Neuraspace_position['dt']['MissDistance']
    
    if flag != 1:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'],
                y=upper_Neuraspace,  # Ignorar pontos com 0
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )

        # Adicionar a banda de erro inferior
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'],
                y=lower_Neuraspace,  
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  
                fillcolor=colorN,  
                showlegend=False
            )
        )
    
    fig.add_trace(
        go.Scatter(
            x=dt_time, y=[warning] * len(dt_time), mode='lines', name='Warning Threshold', line=dict(color='#FFB000', dash='dash'), showlegend=True
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dt_time, y=[alert] * len(dt_time), mode='lines', name='Alert Threshold', line=dict(color='#EA3F6D', dash='dash'), showlegend=True
        )
    )


    for serie in series:
        if flag == 2:
            data = dataSets_position[serie]['dt']['Radial']
            upper = dataSets_position[serie]['upper_bound']['Radial']
            lower = dataSets_position[serie]['lower_bound']['Radial']
            max_value = max([max_value] + data + upper + upper_Neuraspace)
            min_value = min([0] + lower + lower_Neuraspace) 
        elif flag == 3:
            data = dataSets_position[serie]['dt']['AlongTrack']
            upper = dataSets_position[serie]['upper_bound']['AlongTrack']
            lower = dataSets_position[serie]['lower_bound']['AlongTrack']
            max_value = max([max_value] + data + upper + upper_Neuraspace)
            min_value = min([0] + lower + lower_Neuraspace) 
        elif flag == 4:
            data = dataSets_position[serie]['dt']['CrossTrack']
            upper = dataSets_position[serie]['upper_bound']['CrossTrack']
            lower = dataSets_position[serie]['lower_bound']['CrossTrack']
            max_value = max([max_value] + data + upper + upper_Neuraspace)
            min_value = min([0] + lower + lower_Neuraspace) 
        else:
            data = dataSets_position[serie]['dt']['MissDistance']
            max_value = max([max_value] + data)
            min_value = min([min_value] + data)
            


        fig.add_trace(
            go.Scatter(
                x=dataSets_position[serie]['dt_time'], y=data, mode='lines', name=dataSets_position[serie]['name'], line=dict(color=dataSets_position[serie]['color'])
            )   
        )


        if flag != 1:
            # Adicionar a banda de erro superior
            fig.add_trace(
                go.Scatter(
                    x=dataSets_position[serie]['dt_time'],
                    y=upper,  # Ignorar pontos com 0
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                )
            )

            # Adicionar a banda de erro inferior
            fig.add_trace(
                go.Scatter(
                    x=dataSets_position[serie]['dt_time'],
                    y=lower,  
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',  
                    fillcolor=hex_to_rgba(dataSets_position[serie]['color'],0.3),  
                    showlegend=False
                )
            )


    fig.add_shape(
        type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value-100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    if now > tca:
        fig.add_shape(
            type='rect', x0=tca, y0=min_value-100, x1=now, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
            showlegend=False
        )

    fig.add_trace(
        go.Scatter(
            x=Neuraspace_position['dt_time'], y=neura, mode='lines', name=Neuraspace_position['name'], line=dict(color='#000031')
        )
    )
    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            )
        ]
    )    

    fig.update_xaxes(gridcolor='#E5ECF6')

    fig.update_yaxes(gridcolor='#E5ECF6')

    fig.update_layout(plot_bgcolor='white', hovermode="x unified")
    
    fig.update_traces(
        hovertemplate='<br>'.join([
            '<br>'
            'Position: %{y}'
        ]),
    )

@app.callback(
    [Output('multiple_graph', 'figure'),
    Output('button_id2', 'data')],
    [Input('series', 'value'),
     Input('button_id2', 'data'),
     Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks'),
     Input('btn-4', 'n_clicks')]
)
def mainPlot_position2(series, button_id, btn1, btn2, btn3, btn4):
    tca = parser.parse(dataSets_position[list(dataSets_position.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  

    fig = make_subplots()
    colorN = hex_to_rgba('#000031', 0.3)
    min_value = 0
    
    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 2)
        max_value = max(max_values + Neuraspace_position['dt']['Radial'])
        min_value = min(min_values + Neuraspace_position['dt']['Radial'])
        neura = Neuraspace_position['dt']['Radial']
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 3)
        max_value = max(max_values + Neuraspace_position['dt']['AlongTrack'])
        min_value = min(min_values + Neuraspace_position['dt']['AlongTrack'])
        neura = Neuraspace_position['dt']['AlongTrack']
    elif button_id == 'btn-4':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 4)
        max_value = max(max_values + Neuraspace_position['dt']['CrossTrack'])
        min_value = min(min_values + Neuraspace_position['dt']['CrossTrack'])
        neura = Neuraspace_position['dt']['CrossTrack']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 1)
        max_value = max(max_values + Neuraspace_position['dt']['MissDistance'])
        min_value = min(min_values + Neuraspace_position['dt']['MissDistance'])
        neura = Neuraspace_position['dt']['MissDistance']

    max_value = max([max_value]  + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
    min_value = min([min_value] + [dataSets_position[list(dataSets_position.keys())[0]]['Total']['alert'], dataSets_position[list(dataSets_position.keys())[0]]['Total']['warning']])
        
    
    
    if series is None or series == []:
        # lines with x=TCA and x=NOW
        fig.add_shape(
            type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
            name='TCA', showlegend=False
        )
        fig.add_shape(
            type='line', x0=now, y0=min_value-100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
            name='Now',showlegend=False
        )

        # Adding annotations above the TCA and Now lines
        fig.update_layout(
            annotations=[
                dict(
                    x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
                ),
                dict(
                    x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
                )
            ]
        )

        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'], y=neura, mode='lines', name=Neuraspace_position['name'], line=dict(color="#000031", width=2)
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_min, 
                y=min_values,
                line=dict(color='rgba(255,255,255,0)'), showlegend=False, hoverinfo='none')
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_max, 
                y=max_values, fill='tonexty',
                fillcolor='rgba(217,217,217, 0.5)', line=dict(color='rgba(217,217,217, 0.5)'), showlegend=False, hoverinfo='none')
        )
        
        for dataSet in dataSets_position:
            if button_id == 'btn-2':
                data = dataSets_position[dataSet]['dt']['Radial']
            elif button_id == 'btn-3':
                data = dataSets_position[dataSet]['dt']['AlongTrack']
            elif button_id == 'btn-4':
                data = dataSets_position[dataSet]['dt']['CrossTrack']
            else:
                data = dataSets_position[dataSet]['dt']['MissDistance']

            fig.add_trace(
                go.Scatter(
                    x=dataSets_position[dataSet]['dt_time'], y=data, mode='markers', name=dataSets_position[dataSet]['name'], marker=dict(color=dataSets_position[dataSet]['color']))
            )
    
        fig.update_traces(
            hovertemplate='<br>'.join([
                '<br>'
                'Position: %{y}'
        ]),
    )
      
    
    else:
        if button_id == 'btn-2':
            plot_position(fig, series, max_value, colorN, dt_time, 2)
        elif button_id == 'btn-3':
            plot_position(fig, series, max_value, colorN, dt_time, 3)
        elif button_id == 'btn-4':
            plot_position(fig, series, max_value, colorN, dt_time, 4)
        else:
            plot_position(fig, series, max_value, colorN, dt_time, 1)
    

    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(
        plot_bgcolor='white',
        legend=dict(
            x=0,
            y=-1,  # Adjusted to ensure it stays just below the graph
            orientation='h',
            yanchor='bottom',  # Ensure this is consistent with 'y'
            xanchor='left',
            traceorder='normal',
            font=dict(size=10),
            itemwidth=30,
        ),
        margin=dict(l=20, r=20, t=40, b=10),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    return fig, button_id

@app.callback(
    [Output('update_multiple', 'figure'),
     Output('button_m', 'data')],
    [Input('target', 'value'),
    Input('chaser', 'value'),
    Input('update_multiple', 'clickData'),
    Input('button_m', 'data'),
    Input('btn-1', 'n_clicks'),
    Input('btn-2', 'n_clicks'),
    Input('btn-3', 'n_clicks'),
    Input('btn-4', 'n_clicks')
    ]
)
def update_multiple(target, chaser, click_data, button_id, btn1, btn2, btn3, btn4):
    global original_figure

    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  
    n_graphs = len(dataSets_position)

    rows = ceil(n_graphs/3)
    cols = min(4, n_graphs)

    if n_graphs > 2:
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=[('<b>' + dataSets_position[dataSet]['name'] + '</b>') for dataSet in dataSets_position])
    elif n_graphs == 1:
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=[('<b>' + dataSets_position[dataSet]['name'] + '</b>') for dataSet in dataSets_position], vertical_spacing=0.15, horizontal_spacing=0.05)
    else:
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=[('<b>' + dataSets_position[dataSet]['name'] + '</b>') for dataSet in dataSets_position], vertical_spacing=0.15, horizontal_spacing=0.3)
    r = 1
    c = 1

    if button_id == 'btn-2':
        neura = Neuraspace_position['dt']['Radial']
    elif button_id == 'btn-3':
        neura = Neuraspace_position['dt']['AlongTrack']
    elif button_id == 'btn-4':
        neura = Neuraspace_position['dt']['CrossTrack']
    else:
        neura = Neuraspace_position['dt']['MissDistance']
        

    for dataSet in dataSets_position:
        color = hex_to_rgba(dataSets_position[dataSet]['color'], 0.3)

        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'], y=neura, mode='lines', name=Neuraspace_position['name'], line=dict(color='#000031'), showlegend=False
            ), row=r, col=c
        )

        if button_id == 'btn-2':
            data = dataSets_position[dataSet]['dt']['Radial']
        elif button_id == 'btn-3':
            data = dataSets_position[dataSet]['dt']['AlongTrack']
        elif button_id == 'btn-4':
            data = dataSets_position[dataSet]['dt']['CrossTrack']
        else:
            data = dataSets_position[dataSet]['dt']['MissDistance']
            

        fig.add_trace(
            go.Scatter(
                x=dataSets_position[dataSet]['dt_time'], y=data, mode='lines', name=dataSets_position[dataSet]['name'], marker=dict(color=dataSets_position[dataSet]['color']), fill='tonexty', fillcolor=color, showlegend=False
            ), row=r, col=c
        )

        c += 1
        if c > cols:
            c = 1
            r += 1

    for i, title in enumerate(fig['layout']['annotations']):
        fig['layout']['annotations'][i]['font'] = dict(size=10)

    # Dynamically adjust subplot height based on the number of rows
    fig_height = max(200, rows * 200)
    fig.update_layout(height=fig_height, width=cols * 200)

    # Update x and y axes to remove grid lines and tick labels
    fig.update_xaxes(gridcolor='#E5ECF6', showticklabels=False)
    fig.update_yaxes(gridcolor='#E5ECF6')

    # Set overall layout properties
    fig.update_layout(plot_bgcolor='white', font_size=10,
                    margin=dict(l=70, r=70, t=15, b=0))

    original_figure = fig


    if click_data:
        if len(click_data['points']) > 1:
            return original_figure, button_id

        # Highlight the clicked subplot
        point = click_data['points'][0]
        curve_number = point['curveNumber']

        # Determine the subplot index
        subplot_idx = curve_number // 2

        # Calculate row and column based on subplot index
        r = subplot_idx // cols + 1
        c = subplot_idx % cols + 1

        # Get the dataset key for the clicked subplot
        dataset_key = list(dataSets_position.keys())[subplot_idx]

        # Create a new figure with only the clicked subplot
        highlighted_fig = make_subplots(rows=1, cols=1, subplot_titles=[
            ('<b>' + dataSets_position[dataset_key]['name'] + '</b>')])

        highlighted_fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'], y=neura, mode='lines', name=Neuraspace_position['name'], line=dict(color='#000031'), showlegend=True
            ), row=1, col=1
        )

        if button_id == 'btn-2':
            data = dataSets_position[dataset_key]['dt']['Radial']
        elif button_id == 'btn-3':
            data = dataSets_position[dataset_key]['dt']['AlongTrack']
        elif button_id == 'btn-4':
            data = dataSets_position[dataset_key]['dt']['CrossTrack']
        else:
            data = dataSets_position[dataset_key]['dt']['MissDistance']

        color = hex_to_rgba(dataSets_position[dataset_key]['color'], 0.3)
        highlighted_fig.add_trace(
            go.Scatter(
                x=dataSets_position[dataset_key]['dt_time'], y=data, mode='lines', name=dataSets_position[dataset_key]['name'], marker=dict(color=dataSets_position[dataset_key]['color']), fill='tonexty', fillcolor=color, showlegend=True
            ), row=1, col=1
        )

        highlighted_fig.update_layout(height=300, width=700, hovermode='x unified', plot_bgcolor='white',
                                      legend=dict(x=0, y=-0.2, orientation='h', yanchor='bottom', xanchor='left', traceorder='normal', font=dict(size=10), itemwidth=30),
                                      margin=dict(l=100, r=20, t=20, b=40))
        highlighted_fig.update_xaxes(gridcolor='#E5ECF6')
        highlighted_fig.update_yaxes(gridcolor='#E5ECF6')
        highlighted_fig.update_traces(
            hovertemplate='<br>'.join([
                '<br>'
                'Position: %{y}'
            ]),
        )

        return highlighted_fig, button_id

    else:
        return original_figure, button_id
    
   
#Forecast - Use Case 1
def plot_forecast1(fig, value, selected_points, flag, type, forecast_begin):
    forecast_data = {}

    if value == 'Neuraspace':
        d = Neuraspace_forecast
        time = Neuraspace_forecast['dt_time']
        name = Neuraspace_forecast['name']
        color = '#000031'
    else:
        d = dataSets_forecast[value][type]
        time = dataSets_forecast[value][type]['dt_time']
        name = dataSets_forecast[value]['name']
        color = dataSets_forecast[value]['color']
    
    points = {'dt_dt': [], 'dt_time': [], 'dt': []}
    
    points['dt_time'] = list(forecast_begin[value].keys())

    for t in points['dt_time']:
        indice = time.index(t)
        if flag == 1:
            points['dt_dt'].append(d['Radial']['dt'][indice])
        elif flag == 2:
            points['dt_dt'].append(d['AlongTrack']['dt'][indice])
        else:
            points['dt_dt'].append(d['CrossTrack']['dt'][indice])

    if flag == 1:
        data = d['Radial']
        b = 'Radial'
    elif flag == 2:
        data = d['AlongTrack']
        b = 'AlongTrack'
    else:
        data = d['CrossTrack']
        b = 'CrossTrack'

    if time == []:
        fig.add_annotation(
            xref='paper', yref='paper',
            x=0.5, y=0.5,
            text='No data available for the selected series.',
            showarrow=False,
            font=dict(size=20),
            align='center',
            bordercolor='#767689',
        )
    
    else:

        fig.add_trace(
            go.Scatter(
                x= time,
                y= data['dt'],
                mode='lines',
                name=name,
                line=dict(color = color, width=2),  # Definindo apenas a cor e a largura da linha
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=points['dt_time'],
                y=points['dt_dt'],
                mode='markers',
                name='Forecast Selection',
                marker=dict(size=10, color=color, line=dict(color='black', width=1)),
            )
        )
        
        fig.update_layout(
            clickmode='event+select',  # Enable selection of points
        )
        
        selectPoints = selected_points
        
        if len(selectPoints) > 0:
            for forecast in selectPoints:
                for m, f in forecast.items():  
                    forecast_data = {
                        'dt_time': f['dt_time'],
                        'dt': f[b]['dt'],
                        'upper_bound': f[b]['upper_bound'],
                        'lower_bound': f[b]['lower_bound'], 
                        'name': f['name'],
                        'color': f[b]['color'] 
                    }
                    if value != 'Neuraspace':
                        search = dataSets_forecast[value]['Forecast'][type]
                    else:
                        search = Neuraspace_forecast['Forecast']

                    
                    # Forecast
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_data['dt_time'], y=forecast_data['dt'], mode='markers', 
                            marker=dict(size=8, line=dict( color='black', width=1)),
                            name='Forecast ('+forecast_data['name']+')', line=dict(color=forecast_data['color'])
                        )
                    )

                    # Upper Bound
                    fig.add_trace(
                        go.Scatter(
                            name='Upper Bound', x=forecast_data['dt_time'], y=forecast_data['upper_bound'],
                            mode='lines', marker=dict(color=forecast_data['color']), line=dict(width=0),
                            showlegend=False
                        )
                    )

                    # Lower Bound
                    fig.add_trace(
                        go.Scatter(
                            name='Lower Bound', x=forecast_data['dt_time'], y=forecast_data['lower_bound'],
                            mode='lines', marker=dict(color=forecast_data['color']), line=dict(width=0),
                            fillcolor=hex_to_rgba(forecast_data['color'], 0.3), fill='tonexty', showlegend=False
                        )
                    )

def plot_forecast2(fig, selected_datasets, selected_points, flag, type, forecast_begin):
    count_nempty = 0
    for value in selected_datasets:
        forecast_data = {}

        if value == 'Neuraspace':
            d = Neuraspace_forecast
            time = Neuraspace_forecast['dt_time']
            name = Neuraspace_forecast['name']
            color = '#000031'
        else:
            d = dataSets_forecast[value][type]
            time = dataSets_forecast[value][type]['dt_time']
            name = dataSets_forecast[value]['name']
            color = dataSets_forecast[value]['color']
        
        if time != []:
            count_nempty += 1
            
        points = {'dt_dt': [], 'dt_time': [], 'dt': []}
        
        points['dt_time'] = list(forecast_begin[value].keys())

        for t in points['dt_time']:
            indice = time.index(t)
            if flag == 1:
                points['dt_dt'].append(d['Radial']['dt'][indice])
            elif flag == 2:
                points['dt_dt'].append(d['AlongTrack']['dt'][indice])
            else:
                points['dt_dt'].append(d['CrossTrack']['dt'][indice])

        if flag == 1:
            data = d['Radial']
            b = 'Radial'
        elif flag == 2:
            data = d['AlongTrack']
            b = 'AlongTrack'
        else:
            data = d['CrossTrack']
            b = 'CrossTrack'


        fig.add_trace(
            go.Scatter(
                x= time,
                y= data['dt'],
                mode='lines',
                name=name,
                line=dict(color = color, width=2),  # Definindo apenas a cor e a largura da linha
            )
        )

        
        fig.add_trace(
            go.Scatter(
                x=points['dt_time'],
                y=points['dt_dt'],
                mode='markers',
                name='Forecast Selection',
                marker=dict(size=10, color=color, line=dict(color='black', width=1)),
            )
        )

        fig.update_layout(
            clickmode='event+select',  # Enable selection of points
        )

    if count_nempty == 0:
        fig.add_annotation(
                xref='paper', yref='paper',
                x=0.5, y=0.5,
                text='No data available for the selected series.',
                showarrow=False,
                font=dict(size=20),
                align='center',
                bordercolor='#767689',
            )
    
    else:
        selectPoints = selected_points

        if len(selectPoints) > 0:
            for forecast in selectPoints:
                for m, f in forecast.items():  
                    forecast_data = {
                        'dt_time': f['dt_time'],
                        'dt': f[b]['dt'],
                        'upper_bound': f[b]['upper_bound'],
                        'lower_bound': f[b]['lower_bound'], 
                        'name': f['name'],
                        'color': f[b]['color']
                    }
                    
                    if value != 'Neuraspace':
                        search = dataSets_forecast[value]['Forecast'][type]
                    else:
                        search = Neuraspace_forecast['Forecast']
             

                        
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_data['dt_time'], y=forecast_data['dt'], mode='markers', 
                            marker=dict(size=8, line=dict(color='black', width=1)),
                            name='Forecast ('+forecast_data['name']+')', line=dict(color=forecast_data['color'])
                        )
                    )

                    # Upper Bound
                    fig.add_trace(
                        go.Scatter(
                            name='Upper Bound', x=forecast_data['dt_time'], y=forecast_data['upper_bound'],
                            mode='lines', marker=dict(color=forecast_data['color']), line=dict(width=0),
                            showlegend=False
                        )
                    )

                    # Lower Bound
                    fig.add_trace(
                        go.Scatter(
                            name='Lower Bound', x=forecast_data['dt_time'], y=forecast_data['lower_bound'],
                            mode='lines', marker=dict(color=forecast_data['color']), line=dict(width=0),
                            fillcolor=hex_to_rgba(forecast_data['color'], 0.3), fill='tonexty', showlegend=False
                        )
                    )
        
#Chaser
@app.callback(
    [Output('forecast_chaser_graph', 'figure'),
    Output('button_id3', 'data')],
    [Input('selection_series', 'value'),
    Input('selected-points', 'data'),
    Input('button_id3', 'data'), 
    Input('btn-5', 'n_clicks'),
    Input('btn-6', 'n_clicks'),
    Input('btn-7', 'n_clicks')]
)
def update_output(value, selected_points, button_id, btn1, btn2, btn3):
    tca = parser.parse(dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    

    fig = make_subplots()
    min_value = 0

    if button_id == 'btn-6':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 2, 'Chaser')
        max_value = max(max_values + Neuraspace_forecast['AlongTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['AlongTrack']['dt'])
        neura = Neuraspace_forecast['AlongTrack']['dt']
    elif button_id == 'btn-7':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 3, 'Chaser')
        max_value = max(max_values + Neuraspace_forecast['CrossTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['CrossTrack']['dt'])
        neura = Neuraspace_forecast['CrossTrack']['dt']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 1, 'Chaser')
        max_value = max(max_values + Neuraspace_forecast['Radial']['dt'])
        min_value = min(min_values + Neuraspace_forecast['Radial']['dt'])
        neura = Neuraspace_forecast['Radial']['dt']



    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value-100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            )
        ]
    )

    if value is None:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_forecast['dt_time'], y=neura, mode='lines', name=Neuraspace_forecast['name'], line=dict(color='#000031')
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_min, 
                y=min_values,
                line=dict(color='rgba(255,255,255,0)'), showlegend=False, hoverinfo='none')
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_max, 
                y=max_values, fill='tonexty',
                fillcolor='rgba(217,217,217, 0.5)', line=dict(color='rgba(217,217,217, 0.5)'), showlegend=False, hoverinfo='none')
        )
        
        for dataSet in dataSets_forecast:
            if button_id == 'btn-6':
                data = dataSets_forecast[dataSet]['Chaser']['AlongTrack']['dt']
            elif button_id == 'btn-7':
                data = dataSets_forecast[dataSet]['Chaser']['CrossTrack']['dt']
            else:
                data = dataSets_forecast[dataSet]['Chaser']['Radial']['dt']
            fig.add_trace(
                go.Scatter(
                    x=dataSets_forecast[dataSet]['Chaser']['dt_time'], y=data, mode='markers', name=dataSets_forecast[dataSet]['name'], marker=dict(color=dataSets_forecast[dataSet]['color']))
            )

    else:
        if now > tca:
            fig.add_shape(
                type='rect', x0=tca, y0=min_value-100, x1=now, y1=max_value + 100,
                line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
                showlegend=False
            )
        if button_id == 'btn-6':
            plot_forecast1(fig, value, selected_points, 2, 'Chaser', forecast_begin_chaser)
        elif button_id == 'btn-7':
            plot_forecast1(fig, value, selected_points, 3, 'Chaser', forecast_begin_chaser)
        else:
            plot_forecast1(fig, value, selected_points, 1, 'Chaser', forecast_begin_chaser)

        

    fig.update_layout(
        plot_bgcolor='white', legend=dict(x=0.5, y=-0.5, orientation='h', yanchor='top', xanchor='center'),
        margin = dict(l=40, r=40, t=20, b=0),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')

    return fig, button_id

@app.callback(
    [Output('multiple_chaser_graph', 'figure'),
     Output('button_id4', 'data')],
    [Input('compare_series', 'value'),
    Input('selected-points2', 'data'),
    Input('button_id4', 'data'),
    Input('btn-5', 'n_clicks'),
    Input('btn-6', 'n_clicks'),
    Input('btn-7', 'n_clicks')]
)
def update_output2(selected_datasets, selected_points, button_id,  btn1, btn2, btn3):
    tca = parser.parse(dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    min_value = 0

    fig = make_subplots()

    if button_id == 'btn-6':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 2, 'Chaser')
        max_value = max(max_values + Neuraspace_forecast['AlongTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['AlongTrack']['dt'])
        neura = Neuraspace_forecast['AlongTrack']['dt']
    elif button_id == 'btn-7':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 3, 'Chaser')
        max_value = max(max_values + Neuraspace_forecast['CrossTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['CrossTrack']['dt'])
        neura = Neuraspace_forecast['CrossTrack']['dt']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 1, 'Chaser')
        max_value = max(max_values + Neuraspace_forecast['Radial']['dt'])
        min_value = min(min_values + Neuraspace_forecast['Radial']['dt'])
        neura = Neuraspace_forecast['Radial']['dt']

    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value-100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            )
        ]
    )

    if selected_datasets is None or len(selected_datasets) == 0:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_forecast['dt_time'], y=neura, mode='lines', name=Neuraspace_forecast['name'], line=dict(color='#000031')
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_min, 
                y=min_values,
                line=dict(color='rgba(255,255,255,0)'), showlegend=False, hoverinfo='none')
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_max, 
                y=max_values, fill='tonexty',
                fillcolor='rgba(217,217,217, 0.5)', line=dict(color='rgba(217,217,217, 0.5)'), showlegend=False, hoverinfo='none')
        )
        
        for dataSet in dataSets_forecast:
            if button_id == 'btn-6':
                data = dataSets_forecast[dataSet]['Chaser']['AlongTrack']['dt']
            elif button_id == 'btn-7':
                data = dataSets_forecast[dataSet]['Chaser']['CrossTrack']['dt']
            else:
                data = dataSets_forecast[dataSet]['Chaser']['Radial']['dt']
            fig.add_trace(
                go.Scatter(
                    x=dataSets_forecast[dataSet]['Chaser']['dt_time'], y=data, mode='markers', name=dataSets_forecast[dataSet]['name'], marker=dict(color=dataSets_forecast[dataSet]['color']))
            )

    else:
        if now > tca:
            fig.add_shape(
                type='rect', x0=tca, y0=min_value-100, x1=now, y1=max_value + 100,
                line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
                showlegend=False
            )
        if button_id == 'btn-6':
            plot_forecast2(fig, selected_datasets, selected_points, 2, 'Chaser', forecast_begin_chaser)
        elif button_id == 'btn-7':
            plot_forecast2(fig, selected_datasets, selected_points, 3, 'Chaser', forecast_begin_chaser)
        else:
            plot_forecast2(fig, selected_datasets, selected_points, 1, 'Chaser', forecast_begin_chaser)


    fig.update_layout(
        plot_bgcolor='white', legend=dict(x=0.5, y=-0.5, orientation='h', yanchor='top', xanchor='center'),
        margin = dict(l=40, r=40, t=20, b=0),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')

    return fig, button_id

@app.callback(
    Output('selected-points', 'data'),
    Input('selection_series', 'value'),
    Input('forecast_chaser_graph', 'selectedData')
)
def display_selected_data(value, selectedData):
    selected_points = []

    if value is not None:    
        forecast = forecast_begin_chaser[value]
        if selectedData is not None and len(forecast_begin_chaser) > 0:
            for i in selectedData['points']:
                    if i['x'] + '+00:00' in forecast:
                        selected_points.append(forecast[i['x'] + '+00:00'])
            return selected_points
        else:
            return []
    else:
        return []

@app.callback(
    Output('selected-points2', 'data'),
    Input('compare_series', 'value'),
    Input('multiple_chaser_graph', 'selectedData')
)
def display_selected_data2(selected_datasets, selectedData):
    # Initialize selected_points
    selected_points = []

    if selected_datasets is not None and len(selected_datasets) > 0:
        for value in selected_datasets:
            forecast = forecast_begin_chaser[value]
            if selectedData is not None and len(forecast_begin_chaser) > 0:
                for i in selectedData['points']:
                    if i['x'] + '+00:00' in forecast:
                        selected_points.append(forecast[i['x'] + '+00:00'])
            else:
                return []
    return selected_points

#Target
@app.callback(
    [Output('forecast_target_graph', 'figure'),
    Output('button_id5', 'data')],
    [Input('selection_series1', 'value'),
    Input('selected-point3', 'data'),
    Input('button_id5', 'data'), 
    Input('btn-8', 'n_clicks'),
    Input('btn-9', 'n_clicks'),
    Input('btn-10', 'n_clicks')]
)
def update_output3(value, selected_points, button_id, btn1, btn2, btn3):
    tca = parser.parse(dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    min_value = 0

    fig = make_subplots()

    if button_id == 'btn-9':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 2, 'Target')
        max_value = max(max_values + Neuraspace_forecast['AlongTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['AlongTrack']['dt'])
        neura = Neuraspace_forecast['AlongTrack']['dt']
    elif button_id == 'btn-10':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 3, 'Target')
        max_value = max(max_values + Neuraspace_forecast['CrossTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['CrossTrack']['dt'])
        neura = Neuraspace_forecast['CrossTrack']['dt']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 1, 'Target')
        max_value = max(max_values + Neuraspace_forecast['Radial']['dt'])
        min_value = min(min_values + Neuraspace_forecast['Radial']['dt'])
        neura = Neuraspace_forecast['Radial']['dt']

    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value-100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            )
        ]
    )

    if value is None:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_forecast['dt_time'], y=neura, mode='lines', name=Neuraspace_forecast['name'], line=dict(color='#000031')
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_min, 
                y=min_values,
                line=dict(color='rgba(255,255,255,0)'), showlegend=False, hoverinfo='none')
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_max, 
                y=max_values, fill='tonexty',
                fillcolor='rgba(217,217,217, 0.5)', line=dict(color='rgba(217,217,217, 0.5)'), showlegend=False, hoverinfo='none')
        )
        
        for dataSet in dataSets_forecast:
            if button_id == 'btn-9':
                data = dataSets_forecast[dataSet]['Target']['AlongTrack']['dt']
            elif button_id == 'btn-10':
                data = dataSets_forecast[dataSet]['Target']['CrossTrack']['dt']
            else:
                data = dataSets_forecast[dataSet]['Target']['Radial']['dt']
            fig.add_trace(
                go.Scatter(
                    x=dataSets_forecast[dataSet]['Target']['dt_time'], y=data, mode='markers', name=dataSets_forecast[dataSet]['name'], marker=dict(color=dataSets_forecast[dataSet]['color']))
            )

    else:
        if now > tca:
            fig.add_shape(
                type='rect', x0=tca, y0=min_value-100, x1=now, y1=max_value + 100,
                line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
                showlegend=False
            )
        if button_id == 'btn-9':
            plot_forecast1(fig, value, selected_points, 2, 'Target', forecast_begin_target)
        elif button_id == 'btn-10':
            plot_forecast1(fig, value, selected_points, 3, 'Target', forecast_begin_target)
        else:
            plot_forecast1(fig, value, selected_points, 1, 'Target', forecast_begin_target)


    fig.update_layout(
        plot_bgcolor='white', legend=dict(x=0.5, y=-0.5, orientation='h', yanchor='top', xanchor='center'),
        margin = dict(l=40, r=40, t=20, b=0),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')

    return fig, button_id

@app.callback(
    [Output('multiple_target_graph', 'figure'),
     Output('button_id6', 'data')],
    [Input('compare_series1', 'value'),
    Input('selected-points4', 'data'),
    Input('button_id6', 'data'),
    Input('btn-8', 'n_clicks'),
    Input('btn-9', 'n_clicks'),
    Input('btn-10', 'n_clicks')]
)
def update_output4(selected_datasets, selected_points, button_id,  btn1, btn2, btn3):
    tca = parser.parse(dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    min_value = 0

    fig = make_subplots()

    if button_id == 'btn-9':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 2, 'Target')
        max_value = max(max_values + Neuraspace_forecast['AlongTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['AlongTrack']['dt'])
        neura = Neuraspace_forecast['AlongTrack']['dt']
    elif button_id == 'btn-10':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 3, 'Target')
        max_value = max(max_values + Neuraspace_forecast['CrossTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['CrossTrack']['dt'])
        neura = Neuraspace_forecast['CrossTrack']['dt']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 1, 'Target')
        max_value = max(max_values + Neuraspace_forecast['Radial']['dt'])
        min_value = min(min_values + Neuraspace_forecast['Radial']['dt'])
        neura = Neuraspace_forecast['Radial']['dt']

    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value-100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value-100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            )
        ]
    )

    if selected_datasets is None or len(selected_datasets) == 0:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_forecast['dt_time'], y=neura, mode='lines', name=Neuraspace_forecast['name'], line=dict(color='#000031')
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_min, 
                y=min_values,
                line=dict(color='rgba(255,255,255,0)'), showlegend=False, hoverinfo='none')
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time_max, 
                y=max_values, fill='tonexty',
                fillcolor='rgba(217,217,217, 0.5)', line=dict(color='rgba(217,217,217, 0.5)'), showlegend=False, hoverinfo='none')
        )
        
        for dataSet in dataSets_forecast:
            if button_id == 'btn-9':
                data = dataSets_forecast[dataSet]['Target']['AlongTrack']['dt']
            elif button_id == 'btn-10':
                data = dataSets_forecast[dataSet]['Target']['CrossTrack']['dt']
            else:
                data = dataSets_forecast[dataSet]['Target']['Radial']['dt']
            fig.add_trace(
                go.Scatter(
                    x=dataSets_forecast[dataSet]['Target']['dt_time'], y=data, mode='markers', name=dataSets_forecast[dataSet]['name'], marker=dict(color=dataSets_forecast[dataSet]['color']))
            )

    else:
        if now > tca:
            fig.add_shape(
                type='rect', x0=tca, y0=min_value-100, x1=now, y1=max_value + 100,
                line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
                showlegend=False
            )
        if button_id == 'btn-9':
            plot_forecast2(fig, selected_datasets, selected_points, 2, 'Target', forecast_begin_target)
        elif button_id == 'btn-10':
            plot_forecast2(fig, selected_datasets, selected_points, 3, 'Target', forecast_begin_target)
        else:
            plot_forecast2(fig, selected_datasets, selected_points, 1, 'Target', forecast_begin_target)


    fig.update_layout(
        plot_bgcolor='white', legend=dict(x=0.5, y=-0.5, orientation='h', yanchor='top', xanchor='center'),
        margin = dict(l=40, r=40, t=20, b=0),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')

    return fig, button_id

@app.callback(
    Output('selected-point3', 'data'),
    Input('selection_series1', 'value'),
    Input('forecast_target_graph', 'selectedData')
)
def display_selected_data3(value, selectedData):
    selected_points = []

    if value is not None:    
        forecast = forecast_begin_target[value]
        if selectedData is not None and len(forecast_begin_target) > 0:
            for i in selectedData['points']:
                    if i['x'] + '+00:00' in forecast:
                        selected_points.append(forecast[i['x'] + '+00:00'])
            return selected_points
        else:
            return []
    else:
        return []

@app.callback(
    Output('selected-points4', 'data'),
    Input('compare_series1', 'value'),
    Input('multiple_target_graph', 'selectedData')
)
def display_selected_data2(selected_datasets, selectedData):
    # Initialize selected_points
    selected_points = []

    if selected_datasets is not None and len(selected_datasets) > 0:
        for value in selected_datasets:
            forecast = forecast_begin_target[value]
            if selectedData is not None and len(forecast_begin_target) > 0:
                for i in selectedData['points']:
                    if i['x'] + '+00:00' in forecast:
                        selected_points.append(forecast[i['x'] + '+00:00'])
            else:
                return []
    return selected_points

# Run the app
if __name__ == '__main__':
    getcolor()
    forecast_begin_chaser = init_forecast_begin('Chaser', forecast_begin_chaser)
    forecast_begin_target = init_forecast_begin('Target', forecast_begin_target)
    app.run_server(debug=True)