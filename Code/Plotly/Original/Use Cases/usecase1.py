from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import dash
from dateutil import parser
import random

with open('UseCase1_data/data_test.json') as f:
    dataSets_forecast = json.load(f)

with open('UseCase1_data/neuraspace_test.json') as f:
    Neuraspace_forecast = json.load(f)

Neuraspace_forecast["tca"] = dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'], 


now = parser.parse("2024-05-29 19:39:41.572 +0100")

def hex_to_rgba(hex_color, opacity):
    hex_color = hex_color.strip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'

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


app = Dash(__name__)

eixos_ForecastChaser = html.Div([
    html.Button('Radial', id='btn-1', n_clicks=0, className='tab-button'),
    html.Button('Along-track', id='btn-2', n_clicks=0, className='tab-button'),
    html.Button('Cross-track', id='btn-3', n_clicks=0, className='tab-button')
], className='eixos')

app.layout = html.Div([

    html.Div([
        eixos_ForecastChaser,
        html.H3("Chaser Position Uncertainty"),
        dcc.Graph(id='update_plot'),
        
    ]),
    
    dcc.Store(id='button_id', data='btn-1'),  # Store for button id
   
])

#Button active
@app.callback(
    [Output('btn-1', 'className'),
     Output('btn-2', 'className'),
     Output('btn-3', 'className')],
    [Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks')]
)
def update_button_classes_position(btn1, btn2, btn3):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['eixos-button active', 'eixos-button', 'eixos-button']
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return [
            'eixos-button active' if button_id == 'btn-1' else 'eixos-button',
            'eixos-button active' if button_id == 'btn-2' else 'eixos-button',
            'eixos-button active' if button_id == 'btn-3' else 'eixos-button'
        ]


@app.callback(
    [Output('update_plot', 'figure'),
     Output('button_id', 'data')],
    [Input('button_id', 'data'),
     Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks')]
)

def update_plot(button_id, btn1, btn2, btn3):
    fig = make_subplots()

    tca = parser.parse(dataSets_forecast[list(dataSets_forecast.keys())[0]]['tca'])
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[1] == 'n_clicks':
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    

    fig = make_subplots()
    min_value = 0
    colorN = hex_to_rgba('#000031', 0.3)

    
    if button_id == 'btn-2':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 2, 'Chaser')
        neura = Neuraspace_forecast['dt']['AlongTrack']
        max_value = max(max_values + Neuraspace_forecast['dt']['AlongTrack'])
        min_value = min(min_values + Neuraspace_forecast['dt']['AlongTrack'])
        b = 'AlongTrack'
    elif button_id == 'btn-3':
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 3, 'Chaser')
        neura = Neuraspace_forecast['dt']['CrossTrack']
        max_value = max(max_values + Neuraspace_forecast['dt']['CrossTrack'])
        min_value = min(min_values + Neuraspace_forecast['dt']['CrossTrack'])
        b = 'CrossTrack'
    else:
        dt_time_min, min_values, dt_time_max, max_values = get_max_min_forecast(dataSets_forecast, 1, 'Chaser')
        neura = Neuraspace_forecast['dt']['Radial']
        max_value = max(max_values + Neuraspace_forecast['dt']['Radial'])
        min_value = min(min_values + Neuraspace_forecast['dt']['Radial'])
        b = 'Radial'

    fig.add_trace(
        go.Scatter(
            x=Neuraspace_forecast['dt_time'], y=neura, mode='lines', name=Neuraspace_forecast['name'], line=dict(color='#000031')
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
        if button_id == 'btn-2':
            data = dataSets_forecast[dt]['Chaser']['AlongTrack']
            max_value = max([max_value] + data)
            min_value = min([min_value] + data)
        elif button_id == 'btn-3':
            data = dataSets_forecast[dt]['Chaser']['CrossTrack']
            max_value = max([max_value] + data)
            min_value = min([min_value] + data)
        else:
            data = dataSets_forecast[dt]['Chaser']['Radial']
            max_value = max([max_value] + data)
            min_value = min([min_value] + data)
        fig.add_trace(
            go.Scatter(
                x=dataSets_forecast[dt]['Chaser']['dt_time'], y=data, 
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


if __name__ == '__main__':
    forecast_begin_chaser = init_forecast_begin('Chaser', forecast_begin_chaser)
    forecast_begin_target = init_forecast_begin('Target', forecast_begin_target)
    app.run_server(debug=True)