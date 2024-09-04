from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from dateutil import parser
import dash

with open('UseCase2_data/data1.json') as f:
    dataSets_position = json.load(f)

with open('UseCase2_data/neuraspace.json') as f:
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



dt_time = []
min_values, max_values = 0, 0

app = Dash(__name__)

eixos_PositionCase = html.Div([
    html.Button('Miss Distance', id='btn-1', n_clicks=0, className='eixos-button active'),
    html.Button('Radial', id='btn-2', n_clicks=0, className='eixos-button'),
    html.Button('Along-track', id='btn-3', n_clicks=0, className='eixos-button'),
    html.Button('Cross-track', id='btn-4', n_clicks=0, className='eixos-button')
], className='eixos-container')

app.layout = html.Div([
    html.Div([
        eixos_PositionCase,
        html.H3("Position"),
        dcc.Graph(id='update_plot'),
        
    ]),
    
    dcc.Store(id='button_id', data='btn-1'),  # Store for button id
])

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
    [Output('update_plot', 'figure'),
     Output('button_id', 'data')],
    [Input('button_id', 'data'),
     Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks'),
     Input('btn-4', 'n_clicks')]
)

def update_plot(button_id, btn1, btn2, btn3, btn4):
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


if __name__ == '__main__':
    dt_time_min, min_values, dt_time_max, max_values = get_max_min_UC2(dataSets_position, 1)
    app.run_server(debug=True)
