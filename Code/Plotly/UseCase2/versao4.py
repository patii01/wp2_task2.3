#read file json and make it a dictionary
import json
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import dash_bootstrap_components as dbc
import dash
from math import ceil
from dateutil import parser

# Load the data
with open('data/data2.json') as f:
    dataSets = json.load(f)

target_values = list({dataSets[key]['target'] for key in dataSets})
chaser_values = list({dataSets[key]['chaser'] for key in dataSets})
tca = parser.parse(dataSets[list(dataSets.keys())[0]]['tca'])
now = parser.parse("2024-05-30 19:39:41.572 +0100")

dates = []
for key in dataSets:
    for dt_str in dataSets[key]['dt_time']:
        dates.append(datetime.fromisoformat(dt_str).date())

dt_time = list(set(dates))

Neuraspace = {
    "tca": dataSets[list(dataSets.keys())[0]]['tca'], 
    "name": "Neuraspace", 
    "target": "", 
    "chaser": "", 
    "dt_time": ["2024-05-18 01:20:56+00:00", "2024-05-21 17:50:12+00:00", "2024-05-22 17:45:21+00:00", "2024-05-24 00:30:08+00:00"],
    "dt": 
        {
        "MissDistance": [12523.0, 22506.0, 25625.0, 23250.0],
        "AlongTrack": [43751.44316797433, 10224.262204310924, 4468.794925676199, 154.104511147458793], 
        "CrossTrack": [20.40218111919548, 16.912990346290433, 22.080582260212687, 23.080481340273444], 
        "Radial": [145.62077099514772, 86.10936920869318, 70.49559965179682, 70.78340586710809]
        }, 
    "upper_bound": 
        {
        "AlongTrack": [], 
        "CrossTrack": [], 
        "Radial": []
        }, 
    "lower_bound": 
        {
        "AlongTrack": [], 
        "CrossTrack": [], 
        "Radial": []
        }, 
    "Total": 
        {
        "alert": 500, 
        "warning": 1500
        }, 
    "Radial": 
        {"alert": 50, 
        "warning": 100
        }
    }

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

def get_max_min(dataSets, flag):
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

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H3("Position"),
        html.Div([
            html.Button('Miss Distance', id='btn-1', n_clicks=0, className='tab-button active'),
            html.Button('Radial', id='btn-2', n_clicks=0, className='tab-button'),
            html.Button('Along-track', id='btn-3', n_clicks=0, className='tab-button'),
            html.Button('Cross-track', id='btn-4', n_clicks=0, className='tab-button')
        ], className='tab-container')
    ]),
    html.Div([
        dcc.Tabs(id='tabs', value='tab-1', children=[
            dcc.Tab(label='Selection of series', value='tab-1', children=[
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id='target',
                            options=[{'label': i, 'value': i} for i in target_values],
                            placeholder="Source Target")
                    ], className='dropdown-container'),
                    html.Div([
                        dcc.Dropdown(
                            id='chaser',
                            options=[{'label': i, 'value': i} for i in chaser_values],
                            placeholder="Source Chaser")
                    ], className='dropdown-container')
                ]),
                html.Div([
                    dcc.Graph(id='position_graph'),
                ], className='graph'),
                
            ]),

            dcc.Tab(label='Compare multiple series', value='tab-2', children=[
                html.Div([
                    dcc.Dropdown(
                        id='series',
                        options=[{'label': key, 'value': key} for key in dataSets.keys()],
                        placeholder="Select Series",
                        multi=True)
                ], className='dropdown-container'),
                html.Div([
                    dcc.Graph(id='multilple_graph'),
                ], className='graph'),
        
            ]),
            
        ]),
        html.Div([
            dcc.Graph(id='update_multiple')
        ], className='graph_multiple'),
    ], style={'display': 'flex'}),

    dcc.Store(id='button_id', data='btn-1'),  # Store for button id
    dcc.Store(id='button_id2', data='btn-1'),  # Store for button id
])

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

def update_button_classes(btn1, btn2, btn3, btn4):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['tab-button active', 'tab-button', 'tab-button', 'tab-button']
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return [
            'tab-button active' if button_id == 'btn-1' else 'tab-button',
            'tab-button active' if button_id == 'btn-2' else 'tab-button',
            'tab-button active' if button_id == 'btn-3' else 'tab-button',
            'tab-button active' if button_id == 'btn-4' else 'tab-button'
        ]

def plot(fig, target, chaser, max_value, colorN, dt_time, flag):
    min_value = 0
    
    if flag == 2:
        data = dataSets[target + ' vs ' + chaser]['dt']['Radial']
        upper = dataSets[target + ' vs ' + chaser]['upper_bound']['Radial']
        lower = dataSets[target + ' vs ' + chaser]['lower_bound']['Radial']
        upper_Neuraspace = Neuraspace['upper_bound']['Radial']
        lower_Neuraspace = Neuraspace['lower_bound']['Radial']
        warning = dataSets[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace['dt']['Radial']
        max_value = max([max_value] + data + upper + upper_Neuraspace)
        min_value = min([0] + lower + lower_Neuraspace)
    elif flag == 3:
        data = dataSets[target + ' vs ' + chaser]['dt']['AlongTrack']
        upper = dataSets[target + ' vs ' + chaser]['upper_bound']['AlongTrack']
        lower = dataSets[target + ' vs ' + chaser]['lower_bound']['AlongTrack']
        upper_Neuraspace = Neuraspace['upper_bound']['AlongTrack']
        lower_Neuraspace = Neuraspace['lower_bound']['AlongTrack']
        warning = dataSets[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace['dt']['AlongTrack']
        max_value = max([max_value] + data + upper + upper_Neuraspace)
        min_value = min([0] + lower + lower_Neuraspace)
    elif flag == 4:
        data = dataSets[target + ' vs ' + chaser]['dt']['CrossTrack']
        upper = dataSets[target + ' vs ' + chaser]['upper_bound']['CrossTrack']
        lower = dataSets[target + ' vs ' + chaser]['lower_bound']['CrossTrack']
        upper_Neuraspace = Neuraspace['upper_bound']['CrossTrack']
        lower_Neuraspace = Neuraspace['lower_bound']['CrossTrack']
        warning = dataSets[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace['dt']['CrossTrack']
        max_value = max([max_value] + data + upper + upper_Neuraspace)
        min_value = min([0] + lower + lower_Neuraspace)

    else:
        data = dataSets[target + ' vs ' + chaser]['dt']['MissDistance']
        warning = dataSets[target + ' vs ' + chaser]['Total']['warning']
        alert = dataSets[target + ' vs ' + chaser]['Total']['alert']
        neura = Neuraspace['dt']['MissDistance']
        max_value = max([max_value] + data)
        min_value = min([min_value] + data)
    
    fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'], y=neura, mode='lines', name=Neuraspace['name'], line=dict(color='#000031')
            )
    )

    fig.add_trace(
        go.Scatter(
            x=dataSets[target + ' vs ' + chaser]['dt_time'], y=data, mode='lines', name=dataSets[target + ' vs ' + chaser]['name'], line=dict(color=dataSets[target + ' vs ' + chaser]['color'])
        )   
    )


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
    

    if flag != 1:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'],
                y=upper_Neuraspace,  # Ignorar pontos com 0
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )

        # Adicionar a banda de erro inferior
        fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'],
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
                x=dataSets[target + ' vs ' + chaser]['dt_time'],
                y=upper,  # Ignorar pontos com 0
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )

        # Adicionar a banda de erro inferior
        fig.add_trace(
            go.Scatter(
                x=dataSets[target + ' vs ' + chaser]['dt_time'],
                y=lower,  
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  
                fillcolor=hex_to_rgba(dataSets[target + ' vs ' + chaser]['color'], 0.3),  
                showlegend=False
            )
        )

    if now > tca:
        fig.add_shape(
            type='rect', x0=tca, y0=min_value, x1=now, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
            showlegend=False
        )

    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=min_value, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
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

    fig.update_xaxes(gridcolor='#E5ECF6')

    fig.update_yaxes(gridcolor='#E5ECF6')

    fig.update_layout(plot_bgcolor='white', legend=dict(x=0.5, y=-0.3, orientation='h', yanchor='top', xanchor='center'))

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

def update_plot(target, chaser, button_id, btn1, btn2, btn3, btn4):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  
    fig = make_subplots()
    colorN = hex_to_rgba('#000031', 0.3)
    
    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 2)
        max_value = max(max_values + Neuraspace['dt']['Radial'] + [dataSets[list(dataSets.keys())[0]]['Total']['alert'], dataSets[list(dataSets.keys())[0]]['Total']['warning']])
        neura = Neuraspace['dt']['Radial']
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 3)
        max_value = max(max_values + Neuraspace['dt']['AlongTrack'] + [dataSets[list(dataSets.keys())[0]]['Total']['alert'], dataSets[list(dataSets.keys())[0]]['Total']['warning']])
        neura = Neuraspace['dt']['AlongTrack']
    elif button_id == 'btn-4':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 4)
        max_value = max(max_values + Neuraspace['dt']['CrossTrack'] + [dataSets[list(dataSets.keys())[0]]['Total']['alert'], dataSets[list(dataSets.keys())[0]]['Total']['warning']])
        neura = Neuraspace['dt']['CrossTrack']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 1)
        max_value = max(max_values + Neuraspace['dt']['MissDistance'] + [dataSets[list(dataSets.keys())[0]]['Total']['alert'], dataSets[list(dataSets.keys())[0]]['Total']['warning']])
        neura = Neuraspace['dt']['MissDistance']

    
    
    if target is None or chaser is None:

        # lines with x=TCA and x=NOW
        fig.add_shape(
            type='line', x0=tca, y0=0, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
            name='TCA', showlegend=False
        )
        fig.add_shape(
            type='line', x0=now, y0=0, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
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
                x=Neuraspace['dt_time'], y=neura, mode='lines', name=Neuraspace['name'], line=dict(color="#000031", width=2)
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
        
        for dataSet in dataSets:
            if button_id == 'btn-2':
                data = dataSets[dataSet]['dt']['Radial']
            elif button_id == 'btn-3':
                data = dataSets[dataSet]['dt']['AlongTrack']
            elif button_id == 'btn-4':
                data = dataSets[dataSet]['dt']['CrossTrack']
            else:
                data = dataSets[dataSet]['dt']['MissDistance']
            fig.add_trace(
                go.Scatter(
                    x=dataSets[dataSet]['dt_time'], y=data, mode='markers', name=dataSets[dataSet]['name'], marker=dict(color=dataSets[dataSet]['color']))
            )

        ## add text saying "Grey Area: Link between the maximum and minimum position values for each time interval."
        fig.add_annotation(
            xref='paper', yref='paper',
            x=0, y=-1.2,
            text='Grey Area: Link between the maximum and minimum position values for each time interval.',
            showarrow=False,
            font=dict(size=10),
            align='center',
            bordercolor='#767689',
        )
    
    else:
        if target + ' vs ' + chaser not in dataSets:
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
            plot(fig, target, chaser, max_value, colorN, dt_time, 2)
        elif button_id == 'btn-3':
           plot(fig, target, chaser, max_value, colorN, dt_time, 3)
        elif button_id == 'btn-4':
            plot(fig, target, chaser, max_value, colorN, dt_time, 4)
        else:
            plot(fig, target, chaser, max_value, colorN, dt_time, 1)


    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(
        plot_bgcolor='white',
        legend=dict(
            x=0,
            y=-0.4,  # Adjusted to ensure it stays just below the graph
            orientation='h',
            yanchor='bottom',  # Ensure this is consistent with 'y'
            xanchor='left',
            traceorder='normal',
            font=dict(size=10),
            itemwidth=70,
        ),
        margin=dict(l=50, r=20, t=40, b=40),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    return fig, button_id

def plot2(fig, series, max_value, colorN, dt_time, flag):

    warning = Neuraspace['Total']['warning']
    alert = Neuraspace['Total']['alert']
    min_value = 0
    
    if flag == 2:
        upper_Neuraspace = Neuraspace['upper_bound']['Radial']
        lower_Neuraspace = Neuraspace['lower_bound']['Radial']
        neura = Neuraspace['dt']['Radial']
    elif flag == 3:
        upper_Neuraspace = Neuraspace['upper_bound']['AlongTrack']
        lower_Neuraspace = Neuraspace['lower_bound']['AlongTrack']
        neura = Neuraspace['dt']['AlongTrack']
    elif flag == 4:
        upper_Neuraspace = Neuraspace['upper_bound']['CrossTrack']
        lower_Neuraspace = Neuraspace['lower_bound']['CrossTrack']
        neura = Neuraspace['dt']['CrossTrack']
    else:
        neura = Neuraspace['dt']['MissDistance']
    
    if flag != 1:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'],
                y=upper_Neuraspace,  # Ignorar pontos com 0
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )

        # Adicionar a banda de erro inferior
        fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'],
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
            x=dt_time, y=[warning] * len(dt_time), mode='lines', name='Warning Threshold', line=dict(color='#FFB000', dash='dash'), showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dt_time, y=[alert] * len(dt_time), mode='lines', name='Alert Threshold', line=dict(color='#EA3F6D', dash='dash'), showlegend=False
        )
    )

    fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'], y=neura, mode='lines', name=Neuraspace['name'], line=dict(color='#000031')
            )
    )

    for serie in series:
        if flag == 2:
            data = dataSets[serie]['dt']['Radial']
            upper = dataSets[serie]['upper_bound']['Radial']
            lower = dataSets[serie]['lower_bound']['Radial']
            max_value = max([max_value] + data + upper + upper_Neuraspace)
            min_value = min([0] + lower + lower_Neuraspace) 
        elif flag == 3:
            data = dataSets[serie]['dt']['AlongTrack']
            upper = dataSets[serie]['upper_bound']['AlongTrack']
            lower = dataSets[serie]['lower_bound']['AlongTrack']
            max_value = max([max_value] + data + upper + upper_Neuraspace)
            min_value = min([0] + lower + lower_Neuraspace) 
        elif flag == 4:
            data = dataSets[serie]['dt']['CrossTrack']
            upper = dataSets[serie]['upper_bound']['CrossTrack']
            lower = dataSets[serie]['lower_bound']['CrossTrack']
            max_value = max([max_value] + data + upper + upper_Neuraspace)
            min_value = min([0] + lower + lower_Neuraspace) 
        else:
            data = dataSets[serie]['dt']['MissDistance']
            max_value = max([max_value] + data)
            min_value = min([min_value] + data)
            


        fig.add_trace(
            go.Scatter(
                x=dataSets[serie]['dt_time'], y=data, mode='lines', name=dataSets[serie]['name'], line=dict(color=dataSets[serie]['color'])
            )   
        )


        if flag != 1:
            # Adicionar a banda de erro superior
            fig.add_trace(
                go.Scatter(
                    x=dataSets[serie]['dt_time'],
                    y=upper,  # Ignorar pontos com 0
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                )
            )

            # Adicionar a banda de erro inferior
            fig.add_trace(
                go.Scatter(
                    x=dataSets[serie]['dt_time'],
                    y=lower,  
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',  
                    fillcolor=hex_to_rgba(dataSets[serie]['color'],0.3),  
                    showlegend=False
                )
            )


    fig.add_shape(
        type='line', x0=tca, y0=min_value, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=min_value, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    if now > tca:
        fig.add_shape(
            type='rect', x0=tca, y0=min_value, x1=now, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(0.5, 0.5, 0.5, 0.2)', opacity=0.3, layer='below',
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
            )
        ]
    )    

    fig.update_xaxes(gridcolor='#E5ECF6')

    fig.update_yaxes(gridcolor='#E5ECF6')

    fig.update_layout(plot_bgcolor='white', legend=dict(x=0.5, y=-0.3, orientation='h', yanchor='top', xanchor='center'))

@app.callback(
    [Output('multilple_graph', 'figure'),
    Output('button_id2', 'data')],
    [Input('series', 'value'),
     Input('button_id2', 'data'),
     Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks'),
     Input('btn-4', 'n_clicks')]
)

def update_plot2(series, button_id, btn1, btn2, btn3, btn4):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  

    fig = make_subplots()
    colorN = hex_to_rgba('#000031', 0.3)
    
    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 2)
        max_value = max(max_values + Neuraspace['dt']['Radial'])
        neura = Neuraspace['dt']['Radial']
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 3)
        max_value = max(max_values + Neuraspace['dt']['AlongTrack'])
        neura = Neuraspace['dt']['AlongTrack']
    elif button_id == 'btn-4':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 4)
        max_value = max(max_values + Neuraspace['dt']['CrossTrack'])
        neura = Neuraspace['dt']['CrossTrack']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 1)
        max_value = max(max_values + Neuraspace['dt']['MissDistance'])
        neura = Neuraspace['dt']['MissDistance']

    max_value = max([max_value]  + [dataSets[list(dataSets.keys())[0]]['Total']['alert'], dataSets[list(dataSets.keys())[0]]['Total']['warning']])
        
    
    
    if series is None or series == []:
        # lines with x=TCA and x=NOW
        fig.add_shape(
            type='line', x0=tca, y0=0, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
            name='TCA', showlegend=False
        )
        fig.add_shape(
            type='line', x0=now, y0=0, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
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
                x=Neuraspace['dt_time'], y=neura, mode='lines', name=Neuraspace['name'], line=dict(color="#000031", width=2)
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
        
        for dataSet in dataSets:
            if button_id == 'btn-2':
                data = dataSets[dataSet]['dt']['Radial']
            elif button_id == 'btn-3':
                data = dataSets[dataSet]['dt']['AlongTrack']
            elif button_id == 'btn-4':
                data = dataSets[dataSet]['dt']['CrossTrack']
            else:
                data = dataSets[dataSet]['dt']['MissDistance']

            fig.add_trace(
                go.Scatter(
                    x=dataSets[dataSet]['dt_time'], y=data, mode='markers', name=dataSets[dataSet]['name'], marker=dict(color=dataSets[dataSet]['color']))
            )

        ## add text saying "Grey Area: Link between the maximum and minimum position values for each time interval."
        fig.add_annotation(
            xref='paper', yref='paper',
            x=0, y=-1.2,
            text='Grey Area: Link between the maximum and minimum position values for each time interval.',
            showarrow=False,
            font=dict(size=10),
            align='center',
            bordercolor='#767689',
        )
    
    else:
        if button_id == 'btn-2':
            plot2(fig, series, max_value, colorN, dt_time, 2)
        elif button_id == 'btn-3':
            plot2(fig, series, max_value, colorN, dt_time, 3)
        elif button_id == 'btn-4':
            plot2(fig, series, max_value, colorN, dt_time, 4)
        else:
            plot2(fig, series, max_value, colorN, dt_time, 1)
    

    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(
        plot_bgcolor='white',
        legend=dict(
            x=0,
            y=-0.4,  # Adjusted to ensure it stays just below the graph
            orientation='h',
            yanchor='bottom',  # Ensure this is consistent with 'y'
            xanchor='left',
            traceorder='normal',
            font=dict(size=10),
            itemwidth=70,
        ),
        margin=dict(l=50, r=20, t=40, b=40),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    return fig, button_id

@app.callback(
    Output('update_multiple', 'figure'),
    [
    Input('target', 'value'),
    Input('chaser', 'value'),
    Input('btn-1', 'n_clicks'),
    Input('btn-2', 'n_clicks'),
    Input('btn-3', 'n_clicks'),
    Input('btn-4', 'n_clicks')
    ]
)

def update_multiple(target, chaser, btn1, btn2, btn3, btn4):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'btn-1'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    n_graphs = len(dataSets)

    rows = ceil(n_graphs/3)
    cols = min(4, n_graphs)

    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[dataSets[dataSet]['name'] for dataSet in dataSets], vertical_spacing=0.15, horizontal_spacing=0.1)

    r = 1
    c = 1

    if button_id == 'btn-2':
        neura = Neuraspace['dt']['Radial']
    elif button_id == 'btn-3':
        neura = Neuraspace['dt']['AlongTrack']
    elif button_id == 'btn-4':
        neura = Neuraspace['dt']['CrossTrack']
    else:
        neura = Neuraspace['dt']['MissDistance']
        
    

    for dataSet in dataSets:
        color = hex_to_rgba(dataSets[dataSet]['color'], 0.3)

        fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'], y=neura, mode='lines', name=Neuraspace['name'], line=dict(color='#000031'), showlegend=False
            ), row=r, col=c
        )

        if button_id == 'btn-2':
            data = dataSets[dataSet]['dt']['Radial']
        elif button_id == 'btn-3':
            data = dataSets[dataSet]['dt']['AlongTrack']
        elif button_id == 'btn-4':
            data = dataSets[dataSet]['dt']['CrossTrack']
        else:
            data = dataSets[dataSet]['dt']['MissDistance']
            

        fig.add_trace(
            go.Scatter(
                x=dataSets[dataSet]['dt_time'], y=data, mode='lines', name=dataSets[dataSet]['name'], marker=dict(color=dataSets[dataSet]['color']), fill='tonexty', fillcolor=color, showlegend=False
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
                    margin=dict(l=100, r=100, t=15, b=0))

    return fig
    

if __name__ == '__main__':
    app.run_server(debug=True)
