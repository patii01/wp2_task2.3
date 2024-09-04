from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

dataSets = {
    'Neuraspace': {'dt': [1820, 1400, 901, 700, 2290, 1300, 1320], 'color': '#00ACC1', 'name': "Neuraspace", 
                   'dt_time': ['2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06', '2024-04-07'],
                   'upper_bound': [None, None, 1000, 800, None, 1500, 1500], 'lower_bound': [None, None, 800, 650, None, 1000, 1200]}, 
    'HAC': {'dt': [1820, 1400, 931, 700, 2090, 1300], 'color': '#EA1F1F', 'name': "HAC",
              'dt_time': ['2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06'],
              'upper_bound': [None, None, 1000, 800, None, 1500], 'lower_bound': [None, None, 800, 650, None, 1000]},
    'Ephemeris': {'dt': [900, 1900, 950, 1200, 1600, 1320], 'color': '#FA72DC', 'name': "Ephemeris",
              'dt_time': ['2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06', '2024-04-07'],
              'upper_bound': [None, None, 1000, 1300, None, 1500], 'lower_bound': [None, None, 800, 1000, None, 1200]},
    'Space Track': {'dt': [875, 200, 2000, 1950, 1500, 1200], 'color': '#FEB702', 'name': "SpaceTrack",
               'dt_time': ['2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06'],
               'upper_bound': [None, None, 1100, 2000, None, 1500], 'lower_bound': [None, None, 1000, 1050, None, 1000]},
    'EUSST': {'dt': [1300, 500, 400, 800, 1200, 1530], 'color': '#1FEA89', 'name': "EUSST",
               'dt_time': ['2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06'],
               'upper_bound': [None, None, 500, 900, None, 1600], 'lower_bound': [None, None, 300, 650, None, 1000]}
}

now = '2024-04-10'
tca = '2024-04-06'

warning = 500
alert = 2000

newDataSets = {}

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

def calculateAbsoluteDifference():
    for dataSet1 in dataSets:
        if dataSet1 != 'Neuraspace':
            for dataSet2 in dataSets:
                if dataSet2 != 'Neuraspace': #and dataSet2 != dataSet1:
                    newDataSets[dataSet1 + '_' + dataSet2] = {}
                    newDataSets[dataSet1 + '_' + dataSet2]['dt'] = []
                    newDataSets[dataSet1 + '_' + dataSet2]['color'] = mixcolor(dataSet1, dataSet2)
                    newDataSets[dataSet1 + '_' + dataSet2]['name'] = dataSets[dataSet1]['name'] + ' vs ' + dataSets[dataSet2]['name']
                    newDataSets[dataSet1 + '_' + dataSet2]['upper_bound'] = []
                    newDataSets[dataSet1 + '_' + dataSet2]['lower_bound'] = []

                    dt_time = dataSets[dataSet1]['dt_time'] + dataSets[dataSet2]['dt_time']
                    dt_time = list(dict.fromkeys(dt_time))
                    dt_time = sorted(dt_time, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
                    newDataSets[dataSet1 + '_' + dataSet2]['dt_time'] = dt_time

                    # Encontrar os comprimentos das listas
                    len_ub1 = len(dataSets[dataSet1]['upper_bound'])
                    len_ub2 = len(dataSets[dataSet2]['upper_bound'])
                    len_lb1 = len(dataSets[dataSet1]['lower_bound'])
                    len_lb2 = len(dataSets[dataSet2]['lower_bound'])

                    d1up = dataSets[dataSet1]['upper_bound']
                    d2up = dataSets[dataSet2]['upper_bound']
                    d1lo = dataSets[dataSet1]['lower_bound']
                    d2lo = dataSets[dataSet2]['lower_bound']

                    # Preencher com None até que ambas as listas tenham o mesmo comprimento para upper_bound
                    if len_ub1 < len_ub2:
                        d1up = dataSets[dataSet1]['upper_bound'].extend([None] * (len_ub2 - len_ub1))
                    elif len_ub2 < len_ub1:
                        d2up = dataSets[dataSet2]['upper_bound'].extend([None] * (len_ub1 - len_ub2))

                    # Preencher com None até que ambas as listas tenham o mesmo comprimento para lower_bound
                    if len_lb1 < len_lb2:
                        d1lo = dataSets[dataSet1]['lower_bound'].extend([None] * (len_lb2 - len_lb1))
                    elif len_lb2 < len_lb1:
                        d2lo = dataSets[dataSet2]['lower_bound'].extend([None] * (len_lb1 - len_lb2))

                    for time in dt_time:
                        if time in dataSets[dataSet1]['dt_time'] and time in dataSets[dataSet2]['dt_time']:
                            newDataSets[dataSet1 + '_' + dataSet2]['dt'].append(abs(dataSets[dataSet1]['dt'][dataSets[dataSet1]['dt_time'].index(time)] - dataSets[dataSet2]['dt'][dataSets[dataSet2]['dt_time'].index(time)]))
                        elif time in dataSets[dataSet1]['dt_time']:
                            newDataSets[dataSet1 + '_' + dataSet2]['dt'].append(dataSets[dataSet1]['dt'][dataSets[dataSet1]['dt_time'].index(time)])
                        else:
                            newDataSets[dataSet1 + '_' + dataSet2]['dt'].append(dataSets[dataSet2]['dt'][dataSets[dataSet2]['dt_time'].index(time)])
                    
                    for i in range(len(d1lo)):
                        if (d1lo[i] == None and d2lo[i] == None): newDataSets[dataSet1 + '_' + dataSet2]['lower_bound'].append(None)
                        elif (d1lo[i] == None): newDataSets[dataSet1 + '_' + dataSet2]['lower_bound'].append(d2lo[i])
                        elif (d2lo[i] == None): newDataSets[dataSet1 + '_' + dataSet2]['lower_bound'].append(d1lo[i])
                        else: newDataSets[dataSet1 + '_' + dataSet2]['lower_bound'].append(newDataSets[dataSet1 + '_' + dataSet2]['dt'][i] - abs(d1lo[i] - d2lo[i]))
                    for i in range(len(d1up)):
                        if (d1up[i] == None and d2up[i] == None): newDataSets[dataSet1 + '_' + dataSet2]['upper_bound'].append(None)
                        elif (d1up[i] == None): newDataSets[dataSet1 + '_' + dataSet2]['upper_bound'].append(d2up[i])
                        elif (d2up[i] == None): newDataSets[dataSet1 + '_' + dataSet2]['upper_bound'].append(d1up[i])
                        else: newDataSets[dataSet1 + '_' + dataSet2]['upper_bound'].append(newDataSets[dataSet1 + '_' + dataSet2]['dt'][i] + abs(d1up[i] - d2up[i]))                 
               
def get_max_min(dataSets):
    dt_time = []
    for dataSet in dataSets:
        for time in dataSets[dataSet]['dt_time']:
            if time not in dt_time:
                dt_time.append(time)
    
    dt_time = sorted(dt_time, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

    min_values = []
    max_values = []

    for time in dt_time:
        all_values_at_time = []
        for dataSet in dataSets:
            if dataSet != 'Neuraspace':
                if time in dataSets[dataSet]['dt_time']:
                    all_values_at_time.append(dataSets[dataSet]['dt'][dataSets[dataSet]['dt_time'].index(time)])
        if len(all_values_at_time) == 1:
            min_values.append(all_values_at_time[0])
            max_values.append(all_values_at_time[0])
        elif len(all_values_at_time) == 0:
            dt_time.remove(time)
        else:
            min_values.append(min(all_values_at_time))
            max_values.append(max(all_values_at_time))

    return dt_time, min_values, max_values

def mixcolor(dataSet1, dataSet2):
    color1 = dataSets[dataSet1]['color']
    color2 = dataSets[dataSet2]['color']
    
    rgb1 = hexToRgb(color1)
    rgb2 = hexToRgb(color2)

    weight = 0.6

    # Calcula a média dos valores RGB para cada componente de cor
    mixedColor = (
        round((rgb1['r'] + rgb2['r'] * weight) / (1 + weight)), # Componente vermelha
        round((rgb1['g'] + rgb2['g'] * weight) / (1 + weight)), # Componente verde
        round((rgb1['b'] + rgb2['b'] * weight) / (1 + weight))  # Componente azul
    )

    # Converte os valores RGB misturados de volta para o formato hexadecimal
    return rgbToHex(*mixedColor)

dt_time = []
min_values, max_values = 0, 0

app = Dash(__name__)

app.layout = html.Div([
    html.H3("Position"),
    
    dcc.Graph(id='update_plot', style={'height': '400px', 'width': '1300px', 'position': 'relative'}),
])


@app.callback(
    Output('update_plot', 'figure'),
    [Input('update_plot', 'relayoutData')]
)

def update_plot(relayoutData):
    fig = make_subplots()

    fig.add_trace(
        go.Scatter(
            x=dataSets['Neuraspace']['dt_time'], y=dataSets['Neuraspace']['dt'], 
            mode='lines+markers', name=dataSets['Neuraspace']['name'],
            marker=dict(size=10, color=dataSets['Neuraspace']['color']), 
            line=dict(color=dataSets['Neuraspace']['color'])
        )
    )

    for dt in newDataSets:
        fig.add_trace(
            go.Scatter(
                x=newDataSets[dt]['dt_time'], y=newDataSets[dt]['dt'], 
                mode='lines+markers', name=newDataSets[dt]['name'],
                marker=dict(size=10, color=newDataSets[dt]['color']), 
                line=dict(color=newDataSets[dt]['color'])
            )
        )

    max_value = max(max_values + [alert, warning] + dataSets['Neuraspace']['dt'])

    # lines with x=TCA and x=NOW
    fig.add_shape(
        type='line', x0=tca, y0=0, x1=tca, y1=max_value + 100, line=dict(color='red', width=1), 
        name='TCA', showlegend=False
    )
    fig.add_shape(
        type='line', x0=now, y0=0, x1=now, y1=max_value + 100, line=dict(color='grey', width=1), 
        name='Now',showlegend=False
    )

    
    
    tca_plus_72h = (datetime.strptime(tca, '%Y-%m-%d') + timedelta(hours=72)).strftime('%Y-%m-%d')

    dt_copy = set(dt_time + [tca] + [now] + [tca_plus_72h])
    dt_copy = sorted(dt_copy, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    
    fig.add_trace(
        go.Scatter(
            x=dt_copy, y=[warning] * len(dt_copy), mode='lines', name='Warning Threshold', line=dict(color='#EA3F6D', dash='dash')
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dt_copy, y=[alert] * len(dt_copy), mode='lines', name='Alert Threshold', line=dict(color='#FFB000', dash='dash')
        )
    )

    fig.add_shape(
            type='rect', x0=tca, y0=0, x1=tca_plus_72h, y1=max_value + 100,
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
                x=(datetime.strptime(tca, '%Y-%m-%d') + timedelta(hours=24)).strftime('%Y-%m-%d'),
                yref="paper", y=1.05, xref="x", text="72 hours after TCA", showarrow=False
            )
        ]
    )



    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')
    fig.update_layout(plot_bgcolor='white', legend=dict(x=0.5, y=-0.3, orientation='h', yanchor='top', xanchor='center'),
                      margin=dict(r=20, t=20, b=0))

    return fig


if __name__ == '__main__':
    calculateAbsoluteDifference()
    dt_time, min_values, max_values = get_max_min(newDataSets)
    app.run_server(debug=True)
