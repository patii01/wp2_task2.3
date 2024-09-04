import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dcc
from PIL import Image
import json
from dateutil import parser
from datetime import datetime
from datetime import timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import random

STATUS = Image.open("images/status.png")
SATELLITE = Image.open("images/satellite.png")
CONJUCTIONS = Image.open("images/conjuctions.png")
MANOEUVRES = Image.open("images/manoeuvres.png")
FILES = Image.open("images/files.png")
CHAT = Image.open("images/chat.png")
OPERATOR = Image.open("images/operator.png")

with open('UseCase2_data/data_test.json') as f:
    dataSets_position = json.load(f)

with open('UseCase2_data/neuraspace_test.json') as f:
    Neuraspace_position = json.load(f)
Neuraspace_position["tca"] = dataSets_position[list(dataSets_position.keys())[0]]['tca'], 

now = parser.parse("2024-05-29 19:39:41.572 +0100")

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

        if len(all_data_at_date) > 3:
            for i in range(0, len(all_data_at_date), 2):
                subset_data = all_data_at_date[i:i+2]
                subset_times = all_times_at_date[i:i+2]

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


with open('UseCase1_data/data_test.json') as f:
    dataSets_forecast = json.load(f)

with open('UseCase1_data/neuraspace_test.json') as f:
    Neuraspace_forecast = json.load(f)

Neuraspace_forecast["tca"] = dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca']

def get_max_min_forecast(dataSets, flag, type):
    daily_data = {}
    count = 0
    keys = len(dataSets.keys())
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
                        },
                        'CrossTrack': {
                            'dt': model_forecast['CrossTrack']['dt'],
                            'upper_bound': model_forecast['CrossTrack']['upper_bound'],
                            'lower_bound': model_forecast['CrossTrack']['lower_bound'],
                        },
                        'Radial': {
                            'dt': model_forecast['Radial']['dt'],
                            'upper_bound': model_forecast['Radial']['upper_bound'],
                            'lower_bound': model_forecast['Radial']['lower_bound'],
                        }
                    }
    return forecast_begin
  
existing_colors = [dataSets_forecast[key]['color'] for key in dataSets_forecast]
def generate_random_color(existing_colors):
    while True:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        if color not in existing_colors and color != "#000031":
            existing_colors.append(color)
            return color

dt_time = []
min_values, max_values = 0, 0



# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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

eixos_PositionCase = html.Div([
    html.Button('Miss Distance', id='btn-1', n_clicks=0, className='eixos-button active'),
    html.Button('Radial', id='btn-2', n_clicks=0, className='eixos-button'),
    html.Button('Along-track', id='btn-3', n_clicks=0, className='eixos-button'),
    html.Button('Cross-track', id='btn-4', n_clicks=0, className='eixos-button')
], className='eixos-container')

eixos_ForecastChaser = html.Div([
    html.Button('Radial', id='btn-5', n_clicks=0, className='tab-button'),
    html.Button('Along-track', id='btn-6', n_clicks=0, className='tab-button'),
    html.Button('Cross-track', id='btn-7', n_clicks=0, className='tab-button')
], className='eixos')

eixos_ForecastTarget = html.Div([
    html.Button('Radial', id='btn-8', n_clicks=0, className='tab-button'),
    html.Button('Along-track', id='btn-9', n_clicks=0, className='tab-button'),
    html.Button('Cross-track', id='btn-10', n_clicks=0, className='tab-button')
], className='eixos')

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

    html.Div(id="content", className="content", children=[
        html.H3("Evolution"),
        html.Div([
            eixos_PositionCase,
            html.H6("Position"),
            html.Div([
                dcc.Graph(id='position_graph'),
            ], className='graph'),
            
        ]),
        
        dcc.Store(id='button_id1', data='btn-1'),  # Store for button id

        
        html.Div([
            eixos_ForecastChaser,
            html.H6("Chaser Position Uncertainty"),
            html.Div([
                dcc.Graph(id='forecast_chaser_graph'),
            ], className='graph'),
            
        ]),
        
        dcc.Store(id='button_id2', data='btn-5'),  # Store for button id

        html.Div([
            eixos_ForecastTarget,
            html.H6("Target Position Uncertainty"),
            html.Div([
                dcc.Graph(id='forecast_target_graph'),
            ], className='graph'),
            
        ]),
        
        dcc.Store(id='button_id3', data='btn-8'),  # Store for button id



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

#Button active
@app.callback(
    [Output('btn-5', 'className'),
     Output('btn-6', 'className'),
     Output('btn-7', 'className')],
    [Input('btn-5', 'n_clicks'),
     Input('btn-6', 'n_clicks'),
     Input('btn-7', 'n_clicks')]
)
def update_button_chaser_forecast(btn1, btn2, btn3):
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
def update_button_target_forecast(btn1, btn2, btn3):
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


@app.callback(
    [Output('position_graph', 'figure'),
     Output('button_id1', 'data')],
    [Input('button_id1', 'data'),
     Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks'),
     Input('btn-4', 'n_clicks')]
)
def plot_position(button_id, btn1, btn2, btn3, btn4):
    dt_time = []
    min_values, max_values = 0, 0

    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  
    fig = make_subplots()
    colorN = hex_to_rgba('#000031', 0.3)
    warning = Neuraspace_position['Total']['warning']
    alert = Neuraspace_position['Total']['alert']

    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 2)
        neura = Neuraspace_position['dt']['Radial']
        lower_Neura = Neuraspace_position['lower_bound']['Radial']
        upper_Neura = Neuraspace_position['upper_bound']['Radial']
        max_value = max(max_values + [alert, warning] + Neuraspace_position['dt']['Radial'] + upper_Neura)
        min_value = min(min_values + [alert, warning] + Neuraspace_position['dt']['Radial'] + lower_Neura)
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 3)
        neura = Neuraspace_position['dt']['AlongTrack']
        lower_Neura = Neuraspace_position['lower_bound']['AlongTrack']
        upper_Neura = Neuraspace_position['upper_bound']['AlongTrack']
        max_value = max(max_values + [alert, warning] + Neuraspace_position['dt']['AlongTrack'] + upper_Neura)
        min_value = min(min_values + [alert, warning] + Neuraspace_position['dt']['AlongTrack'] + lower_Neura)
    elif button_id == 'btn-4':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 4)
        neura = Neuraspace_position['dt']['CrossTrack']
        lower_Neura = Neuraspace_position['lower_bound']['CrossTrack']
        upper_Neura = Neuraspace_position['upper_bound']['CrossTrack']
        max_value = max(max_values + [alert, warning] + Neuraspace_position['dt']['CrossTrack'] + upper_Neura)
        min_value = min(min_values + [alert, warning] + Neuraspace_position['dt']['CrossTrack'] + lower_Neura)
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 1)
        max_value = max(max_values + [alert, warning] + Neuraspace_position['dt']['MissDistance'])
        min_value = min(min_values + [alert, warning] + Neuraspace_position['dt']['MissDistance'])
        neura = Neuraspace_position['dt']['MissDistance']

    fig.add_trace(
        go.Scatter(
            x=Neuraspace_position['dt_time'], y=neura, 
            mode='lines+markers', name=Neuraspace_position['name'],
            marker=dict(size=10, color='#000031'), 
            line=dict(color='#000031')
        )
    )

    
    if button_id != 'btn-1':
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'],
                y=upper_Neura,  # Ignorar pontos com 0
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )

        # Adicionar a banda de erro inferior
        fig.add_trace(
            go.Scatter(
                x=Neuraspace_position['dt_time'],
                y=lower_Neura,  
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  
                fillcolor=colorN,  
                showlegend=False
            )
        )

        


    for dt in dataSets_position:
        if button_id == 'btn-2':
            data = dataSets_position[dt]['dt']['Radial']
            lower = dataSets_position[dt]['lower_bound']['Radial']
            upper = dataSets_position[dt]['upper_bound']['Radial']
            max_value = max([max_value] + data + upper)
            min_value = min([min_value] + data + lower)
        elif button_id == 'btn-3':
            data = dataSets_position[dt]['dt']['AlongTrack']
            lower = dataSets_position[dt]['lower_bound']['AlongTrack']
            upper = dataSets_position[dt]['upper_bound']['AlongTrack']
            max_value = max([max_value] + data + upper)
            min_value = min([min_value] + data + lower)
        elif button_id == 'btn-4':
            data = dataSets_position[dt]['dt']['CrossTrack']
            lower = dataSets_position[dt]['lower_bound']['CrossTrack']
            upper = dataSets_position[dt]['upper_bound']['CrossTrack']
            max_value = max([max_value] + data + upper)
            min_value = min([min_value] + data + lower)
        else:
            data = dataSets_position[dt]['dt']['MissDistance']
            max_value = max([max_value] + data)
            min_value = min([min_value] + data)
        fig.add_trace(
            go.Scatter(
                x=dataSets_position[dt]['dt_time'], y=data, 
                mode='lines+markers', name=dataSets_position[dt]['name'],
                marker=dict(size=10, color=dataSets_position[dt]['color']), 
                line=dict(color=dataSets_position[dt]['color'])
            )
        )
        if button_id != 'btn-1':
            fig.add_trace(
                go.Scatter(
                    x=dataSets_position[dt]['dt_time'],
                    y=upper,  # Ignorar pontos com 0
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                )
            )

            # Adicionar a banda de erro inferior
            fig.add_trace(
                go.Scatter(
                    x=dataSets_position[dt]['dt_time'],
                    y=lower,  
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',  
                    fillcolor=hex_to_rgba(dataSets_position[dt]['color'], 0.3), 
                    showlegend=False
                )
            )
       
    
    tca = parser.parse(dataSets_position[list(dataSets_position.keys())[0]]['tca'])
    

    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value - 100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value - 100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    
    
    tca_plus_72h = (tca + timedelta(hours=72)).strftime('%Y-%m-%d')

    fig.add_trace(
        go.Scatter(
            x=dt_time, y=[warning] * len(dt_time), mode='lines', name='Warning Threshold', line=dict(color='#FFB000', dash='dash'), showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dt_time, y=[alert] * len(dt_time), mode='lines', name='Alert Threshold', line=dict(color='#EA3F6D', dash='dash'), showlegend=False
        )
    )

    fig.add_shape(
            type='rect', x0=tca, y0=min_value - 150, x1=tca_plus_72h, y1=max_value + 150,
            line=dict(width=0), fillcolor='rgba(239, 247, 257, 0.7)', layer='below',
            showlegend=False
    )

    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            ),
            dict(
                x=tca_plus_72h,
                yref="paper", y=1.08, xref="x", text="72 hours after TCA", showarrow=False
            )
        ]
    )



    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(plot_bgcolor='white', legend=dict(x=0.5, y=-0.3, orientation='h', yanchor='top', xanchor='center'),
                      margin=dict(r=20, t=40, b=0),
                      yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),)

    return fig, button_id

@app.callback(
    [Output('forecast_chaser_graph', 'figure'),
     Output('button_id2', 'data')],
    [Input('button_id2', 'data'),
     Input('btn-5', 'n_clicks'),
     Input('btn-6', 'n_clicks'),
     Input('btn-7', 'n_clicks')]
)

def plot_chaser_forecast(button_id, btn1, btn2, btn3):
    fig = make_subplots()

    tca = parser.parse(dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    

    fig = make_subplots()
    min_value = 0
    colorN = hex_to_rgba('#000031', 0.3)

    
    if button_id == 'btn-6':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 2, 'Chaser')
        neura = Neuraspace_forecast['AlongTrack']
        max_value = max(max_values + Neuraspace_forecast['AlongTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['AlongTrack']['dt'])
        b = 'AlongTrack'
    elif button_id == 'btn-7':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 3, 'Chaser')
        neura = Neuraspace_forecast['CrossTrack']
        max_value = max(max_values + Neuraspace_forecast['CrossTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['CrossTrack']['dt'])
        b = 'CrossTrack'
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 1, 'Chaser')
        neura = Neuraspace_forecast['Radial']
        max_value = max(max_values + Neuraspace_forecast['Radial']['dt'])
        min_value = min(min_values + Neuraspace_forecast['Radial']['dt'])
        b = 'Radial'

    fig.add_trace(
        go.Scatter(
            x=Neuraspace_forecast['dt_time'], y=neura['dt'], mode='lines', name=Neuraspace_forecast['name'], line=dict(color='#000031')
        )
    )


    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value - 100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value - 100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    for dt in dataSets_forecast:
        if button_id == 'btn-6':
            data = dataSets_forecast[dt]['Chaser']['AlongTrack']
            max_value = max([max_value] + data['dt'])
            min_value = min([min_value] + data['dt'])
        elif button_id == 'btn-7':
            data = dataSets_forecast[dt]['Chaser']['CrossTrack']
            max_value = max([max_value] + data['dt'])
            min_value = min([min_value] + data['dt'])
        else:
            data = dataSets_forecast[dt]['Chaser']['Radial']
            max_value = max([max_value] + data['dt'])
            min_value = min([min_value] + data['dt'])
        fig.add_trace(
            go.Scatter(
                x=dataSets_forecast[dt]['Chaser']['dt_time'], y=data['dt'], 
                mode='lines+markers', name=dataSets_forecast[dt]['name'],
                marker=dict(size=10, color=dataSets_forecast[dt]['color']), 
                line=dict(color=dataSets_forecast[dt]['color'])
            )
        )

    
    tca_plus_72h = (tca + timedelta(hours=72)).strftime('%Y-%m-%d')

    fig.add_shape(
            type='rect', x0=tca, y0=min_value - 100, x1=tca_plus_72h, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(239, 247, 257, 0.7)', layer='below',
            showlegend=False
    )

    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            ),
            dict(
                x=tca_plus_72h,
                yref="paper", y=1.08, xref="x", text="72 hours after TCA", showarrow=False
            )
        ]
    )

    for t in forecast_begin_chaser.values():
        for time in t.values():
            for f in time.values():  
                forecast_data = {
                    'dt_time': f['dt_time'],
                    'dt': f[b]['dt'],
                    'upper_bound': f[b]['upper_bound'],
                    'lower_bound': f[b]['lower_bound'], 
                    'name': f['name'], 
                }

                # f['color'] exists
                if 'color' in f:
                    forecast_data['color'] = f['color']
                else:
                    forecast_data['color'] = generate_random_color(existing_colors)
                    f['color'] = forecast_data['color']
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

    
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(plot_bgcolor='white', legend=dict(x=0.5, y=-0.3, orientation='h', yanchor='top', xanchor='center'),
                      margin=dict(r=20, t=40, b=0),
                      yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),)

    return fig, button_id

@app.callback(
    [Output('forecast_target_graph', 'figure'),
     Output('button_id3', 'data')],
    [Input('button_id3', 'data'),
     Input('btn-8', 'n_clicks'),
     Input('btn-9', 'n_clicks'),
     Input('btn-10', 'n_clicks')]
)

def plot_target_forecast(button_id, btn1, btn2, btn3):
    fig = make_subplots()

    tca = parser.parse(dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    

    fig = make_subplots()
    min_value = 0
    colorN = hex_to_rgba('#000031', 0.3)

    
    if button_id == 'btn-9':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 2, 'Target')
        neura = Neuraspace_forecast['AlongTrack']
        max_value = max(max_values + Neuraspace_forecast['AlongTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['AlongTrack']['dt'])
        b = 'AlongTrack'
    elif button_id == 'btn-10':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 3, 'Target')
        neura = Neuraspace_forecast['CrossTrack']
        max_value = max(max_values + Neuraspace_forecast['CrossTrack']['dt'])
        min_value = min(min_values + Neuraspace_forecast['CrossTrack']['dt'])
        b = 'CrossTrack'
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 1, 'Target')
        neura = Neuraspace_forecast['Radial']
        max_value = max(max_values + Neuraspace_forecast['Radial']['dt'])
        min_value = min(min_values + Neuraspace_forecast['Radial']['dt'])
        b = 'Radial'

    fig.add_trace(
        go.Scatter(
            x=Neuraspace_forecast['dt_time'], y=neura['dt'], mode='lines', name=Neuraspace_forecast['name'], line=dict(color='#000031')
        )
    )


    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value - 100, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value - 100, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    for dt in dataSets_forecast:
        if button_id == 'btn-9':
            data = dataSets_forecast[dt]['Target']['AlongTrack']
            max_value = max([max_value] + data['dt'])
            min_value = min([min_value] + data['dt'])
        elif button_id == 'btn-10':
            data = dataSets_forecast[dt]['Target']['CrossTrack']
            max_value = max([max_value] + data['dt'])
            min_value = min([min_value] + data['dt'])
        else:
            data = dataSets_forecast[dt]['Target']['Radial']
            max_value = max([max_value] + data['dt'])
            min_value = min([min_value] + data['dt'])
        fig.add_trace(
            go.Scatter(
                x=dataSets_forecast[dt]['Target']['dt_time'], y=data['dt'], 
                mode='lines+markers', name=dataSets_forecast[dt]['name'],
                marker=dict(size=10, color=dataSets_forecast[dt]['color']), 
                line=dict(color=dataSets_forecast[dt]['color'])
            )
        )

    
    tca_plus_72h = (tca + timedelta(hours=72)).strftime('%Y-%m-%d')

    fig.add_shape(
            type='rect', x0=tca, y0=min_value - 100, x1=tca_plus_72h, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(239, 247, 257, 0.7)', layer='below',
            showlegend=False
    )

    # Adding annotations above the TCA and Now lines
    fig.update_layout(
        annotations=[
            dict(
                x=tca, yref="paper", y=1.1, xref="x", text="TCA", showarrow=False
            ),
            dict(
                x=now, yref="paper", y=1.1, xref="x", text="Now", showarrow=False
            ),
            dict(
                x=tca_plus_72h,
                yref="paper", y=1.08, xref="x", text="72 hours after TCA", showarrow=False
            )
        ]
    )

    for t in forecast_begin_target.values():
        for time in t.values():
            for f in time.values():  
                forecast_data = {
                    'dt_time': f['dt_time'],
                    'dt': f[b]['dt'],
                    'upper_bound': f[b]['upper_bound'],
                    'lower_bound': f[b]['lower_bound'], 
                    'name': f['name'], 
                }

                # f['color'] exists
                if 'color' in f:
                    forecast_data['color'] = f['color']
                else:
                    forecast_data['color'] = generate_random_color(existing_colors)
                    f['color'] = forecast_data['color']
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

    
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(plot_bgcolor='white', legend=dict(x=0.5, y=-0.3, orientation='h', yanchor='top', xanchor='center'),
                      margin=dict(r=20, t=40, b=0),
                      yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),)

    return fig, button_id




if __name__ == "__main__":
    forecast_begin_chaser = init_forecast_begin('Chaser', forecast_begin_chaser)
    forecast_begin_target = init_forecast_begin('Target', forecast_begin_target)
    app.run_server(debug=True)