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
import random

# Load the data
with open('data/data1.json') as f:
    dataSets = json.load(f)

target_chaser_values = list({dataSets[key]['name'] for key in dataSets})
target_chaser_values.append('Neuraspace')
tca = parser.parse(dataSets[list(dataSets.keys())[0]]['tca'])
now = parser.parse("2024-05-26 19:39:41.572 +0100")

Neuraspace = {
    "tca": "2024-05-25 07:36:59.109000+00:00", 
    "name": "Neuraspace", 
    "dt_time": ["2024-05-22 14:30:12+00:00", "2024-05-22 17:45:21+00:00", "2024-05-24 00:30:08+00:00"],
    "dt": {
        "AlongTrack": [10224.262204310924, 4468.794925676199, 154.104511147458793], 
        "CrossTrack": [16.912990346290433, 22.080582260212687, 23.080481340273444], 
        "Radial": [86.10936920869318, 74.49559965179682, 70.78340586710809]}, 
    
    "Forecast": {
        0.0: {
            'dt_time': [],
            "AlongTrack": {"dt": [], "upper_bound": [], "lower_bound": []}, 
            "CrossTrack": {"dt": [], "upper_bound": [], "lower_bound": []}, 
            "Radial": {"dt": [], "upper_bound": [], "lower_bound": []}}
    }
}

forecast_begin = {}

def hex_to_rgba(hex_color, opacity):
    hex_color = hex_color.strip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'

def find_closest_before(target_time, times):
    target_dt = datetime.fromisoformat(target_time)
    closest_time = None
    for time in times:
        dt = datetime.fromisoformat(time)
        if dt <= target_dt:
            if closest_time is None or dt > datetime.fromisoformat(closest_time):
                closest_time = time
    return closest_time

def init_forecast_begin_chaser():
    dataSets_for_forecast = dataSets.copy()
    dataSets_for_forecast['Neuraspace'] = Neuraspace
    for dataset in dataSets_for_forecast:
        forecast_begin[dataset] = {}
        if dataset != 'Neuraspace':
            dt = dataSets_for_forecast[dataset]['Forecast']['Chaser']
            times = dataSets_for_forecast[dataset]['Chaser']['dt_time']
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
             
def get_max_min(dataSets, flag, type):
    daily_data = {}
    count = 0
    for dataSet in dataSets.values():
        count += 1
        for idx, time in enumerate(dataSet[type]['dt_time']):
            date_str = datetime.fromisoformat(time).date()  # Extract the date part
            data = 0
            if date_str not in daily_data:
                daily_data[date_str] = []
            
            if flag == 1:
                data = dataSet[type]['Radial'][idx]
            elif flag == 2:
                data = dataSet[type]['AlongTrack'][idx]
            else:
                data = dataSet[type]['CrossTrack'][idx]
            
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

existing_colors = [dataSets[key]['color'] for key in dataSets]
def generate_random_color(existing_colors):
    while True:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        if color not in existing_colors and color != "#000031":
            existing_colors.append(color)
            return color


app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H3("Chaser Position Uncertainty"),
        html.Div([
            html.Button('Radial', id='btn-1', n_clicks=0, className='tab-button'),
            html.Button('Along-track', id='btn-2', n_clicks=0, className='tab-button'),
            html.Button('Cross-track', id='btn-3', n_clicks=0, className='tab-button')
        ], className='eixos')
    ]),

    html.Div([
        dcc.Tabs(id='tabs', value='tab-1', children=[
            dcc.Tab(label='Selection of series', value='tab-1', children=[
                html.Div([
                    dcc.Dropdown(
                        id='selection',
                        options=[{'label': i, 'value': i} for i in target_chaser_values],
                        placeholder="Source Chaser",
                    )
                ]),
                html.Div([
                    dcc.Graph(id='update_plot'),
                ], className='graph'), 
            ]),
            dcc.Tab(label='Selection of multiple series', value='tab-2', children=[
                html.Div([
                    dcc.Dropdown(
                        id='compare_series',
                        options=[{'label': i, 'value': i} for i in target_chaser_values],
                        placeholder="Selection of series",
                        multi=True,
                    ),
                ]),
                html.Div([
                    dcc.Graph(id='update_plot2'),
                ], className='graph'), 
            ]),
        
        ]),
    ], style={'margin-top': '70px'}),

    dcc.Store(id='button_id', data='btn-1'),  # Store for button id
    dcc.Store(id='button_id2', data='btn-1'),  # Store for button id
    dcc.Store(id='selected-points', data=[]),  # Store for selected points
    dcc.Store(id='selected-points2', data=[])  # Store for selected points
])

@app.callback(
    [Output('btn-1', 'className'),
     Output('btn-2', 'className'),
     Output('btn-3', 'className')],
    [Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks')]
)
def update_button_classes(btn1, btn2, btn3):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['tab-button active', 'tab-button', 'tab-button']
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return [
            'tab-button active' if button_id == 'btn-1' else 'tab-button',
            'tab-button active' if button_id == 'btn-2' else 'tab-button',
            'tab-button active' if button_id == 'btn-3' else 'tab-button',
        ]

def plot(fig, value, selected_points, flag, type):
    forecast_data = {}

    if value == 'Neuraspace':
        d = Neuraspace['dt']
        time = Neuraspace['dt_time']
        name = Neuraspace['name']
        color = '#000031'
    else:
        d = dataSets[value][type]
        time = dataSets[value][type]['dt_time']
        name = dataSets[value]['name']
        color = dataSets[value]['color']
    
    points = {'dt_dt': [], 'dt_time': [], 'dt': []}
    
    points['dt_time'] = list(forecast_begin[value].keys())

    for t in points['dt_time']:
        indice = time.index(t)
        if flag == 1:
            points['dt_dt'].append(d['Radial'][indice])
        elif flag == 2:
            points['dt_dt'].append(d['AlongTrack'][indice])
        else:
            points['dt_dt'].append(d['CrossTrack'][indice])

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
            y= data,
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
            for f in forecast.values():  
                forecast_data = {
                    'dt_time': f['dt_time'],
                    'dt': f[b]['dt'],
                    'upper_bound': f[b]['upper_bound'],
                    'lower_bound': f[b]['lower_bound'], 
                    'name': f['name'], 
                    'color': ''
                }
                if forecast_data['color'] == '':
                    forecast_data['color'] = generate_random_color(existing_colors)
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


@app.callback(
    [Output('update_plot', 'figure'),
    Output('button_id', 'data')],
    [Input('selection', 'value'),
    Input('selected-points', 'data'),
    Input('button_id', 'data'), 
    Input('btn-1', 'n_clicks'),
    Input('btn-2', 'n_clicks'),
    Input('btn-3', 'n_clicks')]
)
def update_output(value, selected_points, button_id, btn1, btn2, btn3):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  

    fig = make_subplots()

    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 2, 'Chaser')
        max_value = max(max_values + Neuraspace['dt']['AlongTrack'])
        neura = Neuraspace['dt']['AlongTrack']
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 3, 'Chaser')
        max_value = max(max_values + Neuraspace['dt']['CrossTrack'])
        neura = Neuraspace['dt']['CrossTrack']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 1, 'Chaser')
        max_value = max(max_values + Neuraspace['dt']['Radial'])
        neura = Neuraspace['dt']['Radial']

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

    if value is None:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'], y=neura, mode='lines', name=Neuraspace['name'], line=dict(color='#000031')
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
                data = dataSets[dataSet]['Chaser']['AlongTrack']
            elif button_id == 'btn-3':
                data = dataSets[dataSet]['Chaser']['CrossTrack']
            else:
                data = dataSets[dataSet]['Chaser']['Radial']
            fig.add_trace(
                go.Scatter(
                    x=dataSets[dataSet]['Chaser']['dt_time'], y=data, mode='markers', name=dataSets[dataSet]['name'], marker=dict(color=dataSets[dataSet]['color']))
            )

    else:
        if button_id == 'btn-2':
            plot(fig, value, selected_points, 2, 'Chaser')
        elif button_id == 'btn-3':
            plot(fig, value, selected_points, 3, 'Chaser')
        else:
            plot(fig, value, selected_points, 1, 'Chaser')


    fig.update_layout(
        plot_bgcolor='white', legend=dict(x=0.5, y=-0.5, orientation='h', yanchor='top', xanchor='center'),
        margin = dict(l=40, r=40, t=40, b=0),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')

    return fig, button_id

def plot2(fig, selected_datasets, selected_points, flag, type):
    for value in selected_datasets:
        forecast_data = {}

        if value == 'Neuraspace':
            d = Neuraspace['dt']
            time = Neuraspace['dt_time']
            name = Neuraspace['name']
            color = '#000031'
        else:
            d = dataSets[value][type]
            time = dataSets[value][type]['dt_time']
            name = dataSets[value]['name']
            color = dataSets[value]['color']
        
        points = {'dt_dt': [], 'dt_time': [], 'dt': []}
        
        points['dt_time'] = list(forecast_begin[value].keys())

        for t in points['dt_time']:
            indice = time.index(t)
            if flag == 1:
                points['dt_dt'].append(d['Radial'][indice])
            elif flag == 2:
                points['dt_dt'].append(d['AlongTrack'][indice])
            else:
                points['dt_dt'].append(d['CrossTrack'][indice])

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
                y= data,
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
            for f in forecast.values():  
                forecast_data = {
                    'dt_time': f['dt_time'],
                    'dt': f[b]['dt'],
                    'upper_bound': f[b]['upper_bound'],
                    'lower_bound': f[b]['lower_bound'], 
                    'name': f['name'], 
                    'color': ''
                }
                if forecast_data['color'] == '':
                    forecast_data['color'] = generate_random_color(existing_colors)
                    
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
    
@app.callback(
    [Output('update_plot2', 'figure'),
     Output('button_id2', 'data')],
    [Input('compare_series', 'value'),
    Input('selected-points2', 'data'),
    Input('button_id2', 'data'),
    Input('btn-1', 'n_clicks'),
    Input('btn-2', 'n_clicks'),
    Input('btn-3', 'n_clicks')]
)
def update_output2(selected_datasets, selected_points, button_id,  btn1, btn2, btn3):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  
    fig = make_subplots()

    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 2, 'Chaser')
        max_value = max(max_values + Neuraspace['dt']['AlongTrack'])
        neura = Neuraspace['dt']['AlongTrack']
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 3, 'Chaser')
        max_value = max(max_values + Neuraspace['dt']['CrossTrack'])
        neura = Neuraspace['dt']['CrossTrack']
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min(dataSets, 1, 'Chaser')
        max_value = max(max_values + Neuraspace['dt']['Radial'])
        neura = Neuraspace['dt']['Radial']

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

    if selected_datasets is None or len(selected_datasets) == 0:
        fig.add_trace(
            go.Scatter(
                x=Neuraspace['dt_time'], y=neura, mode='lines', name=Neuraspace['name'], line=dict(color='#000031')
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
                data = dataSets[dataSet]['Chaser']['AlongTrack']
            elif button_id == 'btn-3':
                data = dataSets[dataSet]['Chaser']['CrossTrack']
            else:
                data = dataSets[dataSet]['Chaser']['Radial']
            fig.add_trace(
                go.Scatter(
                    x=dataSets[dataSet]['Chaser']['dt_time'], y=data, mode='markers', name=dataSets[dataSet]['name'], marker=dict(color=dataSets[dataSet]['color']))
            )

    else:
        if button_id == 'btn-2':
            plot2(fig, selected_datasets, selected_points, 2, 'Chaser')
        elif button_id == 'btn-3':
            plot2(fig, selected_datasets, selected_points, 3, 'Chaser')
        else:
            plot2(fig, selected_datasets, selected_points, 1, 'Chaser')


    fig.update_layout(
        plot_bgcolor='white', legend=dict(x=0.5, y=-0.5, orientation='h', yanchor='top', xanchor='center'),
        margin = dict(l=40, r=40, t=40, b=0),
        yaxis=dict(tickformat='.0f', tickprefix='', ticksuffix=' m'),
    )
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')

    return fig, button_id

@app.callback(
    Output('selected-points', 'data'),
    Input('selection', 'value'),
    Input('update_plot', 'selectedData')
)
def display_selected_data(value, selectedData):
    selected_points = []

    if value is not None:    
        forecast = forecast_begin[value]
        if selectedData is not None and len(forecast_begin) > 0:
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
    Input('update_plot2', 'selectedData')
)
def display_selected_data2(selected_datasets, selectedData):
    # Initialize selected_points
    selected_points = []

    if selected_datasets is not None and len(selected_datasets) > 0:
        for value in selected_datasets:
            forecast = forecast_begin[value]
            if selectedData is not None and len(forecast_begin) > 0:
                for i in selectedData['points']:
                    if i['x'] + '+00:00' in forecast:
                        selected_points.append(forecast[i['x'] + '+00:00'])
            else:
                return []
    return selected_points

if __name__ == '__main__':
    init_forecast_begin_chaser()
    app.run_server(debug=True)
