from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime

dataSets = {
    'Neuraspace': {'dt': [1820, 1400, 901, 700, 2290, 1300, 1320], 'color': '#00ACC1', 'name': "Neuraspace", 
                   'dt_time': ['2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06', '2024-04-07']}, 
    'HAC': {'dt': [1820, 1400, 931, 2090, 1300], 'color': '#EA1F1F', 'name': "HAC",
              'dt_time': ['2024-04-01', '2024-04-02', '2024-04-04', '2024-04-05', '2024-04-06']},
    'Ephemeris': {'dt': [900, 1900, 950, 1200, 1600, 1320], 'color': '#FA72DC', 'name': "Ephemeris",
              'dt_time': ['2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06', '2024-04-07']},
    'Space Track': {'dt': [875, 200, 2000, 1950, 1500, 1200], 'color': '#FEB702', 'name': "SpaceTrack",
               'dt_time': ['2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06']},
    'EUSST': {'dt': [1300, 500, 400, 800, 2000, 1530], 'color': '#1FEA89', 'name': "EUSST",
               'dt_time': ['2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06']}
}

forecasts = {
    'forecast1': {'dt': [1050, 1040, 1030, 1020, 1010, 1000, 990, 980, 970, 960, 950, 940, 930, 920, 910], 'color': '#dcea1f', 'name': "Forecast",
             'dt_time': ['2024-04-04 09:05:49', '2024-04-04 14:03:25', '2024-04-04 17:01:01', '2024-04-04 20:58:37', '2024-04-04 22:56:13', 
                         '2024-04-05 09:05:49', '2024-04-05 14:03:25', '2024-04-05 17:01:01', '2024-04-05 20:58:37', '2024-04-05 22:56:13', 
                         '2024-04-06 07:53:49', '2024-04-06 11:51:25', '2024-04-06 14:49:01', '2024-04-06 18:46:37', '2024-04-06 20:46:37'],
             'upper_bound': [1250, 1240, 1230, 1220, 1210, 1200, 1190, 1180, 1170, 1160, 1150, 1140, 1130, 1120, 1110],
             'lower_bound': [850, 840, 830, 820, 810, 800, 790, 780, 770, 760, 750, 740, 730, 720, 710]},

    'forecast2': {'dt': [1000, 990, 980, 970, 960, 950, 940, 930, 920, 910], 'color': '#701fbe', 'name': "Forecast",
             'dt_time': ['2024-04-05 09:05:49', '2024-04-05 14:03:25', '2024-04-05 17:01:01', '2024-04-05 20:58:37', '2024-04-05 22:56:13', 
                         '2024-04-06 07:53:49', '2024-04-06 11:51:25', '2024-04-06 14:49:01', '2024-04-06 18:46:37', '2024-04-06 20:46:37'],
             'upper_bound': [1200, 1190, 1180, 1170, 1160, 1150, 1140, 1130, 1120, 1110],
             'lower_bound': [800, 790, 780, 770, 760, 750, 740, 730, 720, 710]},

    'forecast3': {'dt': [900, 890, 880, 870, 860, 850, 840, 830, 820], 'color': '#00FF00', 'name': "Forecast",
             'dt_time': ['2024-04-05 14:03:25', '2024-04-05 17:01:01', '2024-04-05 20:58:37', '2024-04-05 22:56:13', 
                         '2024-04-06 07:53:49', '2024-04-06 11:51:25', '2024-04-06 14:49:01', '2024-04-06 18:46:37', '2024-04-06 20:46:37'],
             'upper_bound': [1190, 1180, 1170, 1160, 1150, 1140, 1130, 1120, 1110],
             'lower_bound': [790, 780, 770, 760, 750, 740, 730, 720, 710]}

}

forecast_begin = {}

tca = '2024-04-09'
now = '2024-04-07'

def hex_to_rgba(hex_color, opacity):
    hex_color = hex_color.strip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'

def init_forecast_begin():
    for key in forecasts.keys():
        forecast_date = forecasts[key]['dt_time'][0].split(' ')[0]
        if forecast_date not in forecast_begin.keys():
            forecast_begin[forecast_date] = [key]
        else: 
            forecast_begin[forecast_date].append(key)

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

dt_time = []
min_values, max_values = 0, 0

app = Dash(__name__)

app.layout = html.Div([
    html.H3("Chaser Position Uncertainty"),
    
    dcc.Dropdown(
        id='dataset',
        options=[{'label': i, 'value': i} for i in dataSets.keys()],
        style={'width': '200px'},
        placeholder="Source Chaser",
    ),

    dcc.Graph(id='update_plot', style={'height': '400px', 'width': '1300px', 'position': 'relative', 'z-index': '2'}),

    html.Div(id='graph-container', children=[
        dcc.Graph(id='update_forecast', style={'height': '200px', 'width': '1300px', 'margin-top': '-100px', 'position': 'relative', 'z-index': '1'}),
    ]),
    
    dcc.Store(id='selected-points', data=[])  # Store for selected points
])

@app.callback(
    Output('graph-container', 'style'),
    Input('dataset', 'value')
)
def show_graph(value):
    if value is None:
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    Output('update_forecast', 'figure'),
    Input('dataset', 'value')
)

def update_forecast(value):

    if value is not None:
        fig = make_subplots()

        data = dataSets[value]

        fig.add_trace(
            go.Scatter(
                x=data['dt_time'], y=[0]*len(data['dt_time']), mode='lines+markers', name='', marker=dict(size=10, color=data['color'], line=dict( color='black', width=1)),
            )
        )

        fig.update_yaxes(visible=False)

        fig.update_layout(
            clickmode='event+select',  # Enable selection of points
            plot_bgcolor='white'

        )

        fig.update_xaxes(range=[data['dt_time'][0], max(dt_time[-1], now, tca)], showticklabels=False)

        #add title in the bottom
        fig.add_annotation(
            x=0.5,
            y=-2,
            xref='paper',
            yref='paper',
            text='Selection of Forecast',
            showarrow=False,
            font=dict(size=14),
            font_family="sans-serif",
            font_color="#767689",
        )

        return fig
    else:
        return {}
  
@app.callback(
    Output('selected-points', 'data'),
    Input('dataset', 'value'),
    Input('update_forecast', 'selectedData')
)
def display_selected_data(value, selectedData):
    if value is not None:
        data = dataSets[value]
        if selectedData is not None:
            selected_points = [data['dt_time'][i['pointIndex']] for i in selectedData['points']]
            return selected_points
        else:
            return []
    else:
        return []

@app.callback(
    Output('update_plot', 'figure'),
    Input('dataset', 'value'),
    Input('selected-points', 'data')
)
def update_output(value, selected_points):

    fig = make_subplots()

    if value is None:
        fig.add_trace(
            go.Scatter(
                x=dataSets['Neuraspace']['dt_time'], y=dataSets['Neuraspace']['dt'], mode='lines', name=dataSets['Neuraspace']['name'], line=dict(color=dataSets['Neuraspace']['color'])
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dt_time + dt_time[::-1], 
                y=min_values + max_values[::-1], fill='toself',
                fillcolor='rgba(217,217,217, 0.5)', line=dict(color='rgba(255,255,255,0)'), showlegend=False, hoverinfo='none')
        )
        
        for dataSet in dataSets:
            if dataSet != 'Neuraspace':
                fig.add_trace(
                    go.Scatter(
                        x=dataSets[dataSet]['dt_time'], y=dataSets[dataSet]['dt'], mode='markers', name=dataSets[dataSet]['name'], marker=dict(color=dataSets[dataSet]['color']))
                )

    else:
        data = dataSets[value]

        fig.add_trace(
            go.Scatter(
                x=data['dt_time'], y=data['dt'], mode='lines', name=data['name'], line=dict(color=data['color'])
            )
        )

        if len(selected_points) > 0:
            for i in selected_points:
                if i in forecast_begin.keys():
                    for f in forecast_begin[i]:
                        forecast_data = forecasts[f]
                        # Forecast
                        fig.add_trace(
                            go.Scatter(
                                x=forecast_data['dt_time'], y=forecast_data['dt'], mode='markers', 
                                marker=dict(size=8, line=dict( color='black', width=1)),
                                name=forecast_data['name'], line=dict(color=forecast_data['color'])
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

    max_value = max(max_values + dataSets['Neuraspace']['dt'])
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

    if datetime.strptime(now, '%Y-%m-%d') < datetime.strptime(tca, '%Y-%m-%d'):
        fig.add_shape(
            type='rect', x0=tca, y0=0, x1=now, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(0, 255, 0, 0.1)', opacity=0.3, layer='below',
            showlegend=False
        )

    if datetime.strptime(now, '%Y-%m-%d') > datetime.strptime(tca, '%Y-%m-%d'):
        fig.add_shape(
            type='rect', x0=tca, y0=0, x1=now, y1=max_value + 100,
            line=dict(width=0), fillcolor='rgba(255, 0, 0, 0.1)', opacity=0.3, layer='below',
            showlegend=False
        )

    fig.update_layout(
        plot_bgcolor='white', legend=dict(x=0.5, y=-0.3, orientation='h', yanchor='top', xanchor='center')
    )
    fig.update_xaxes(gridcolor='#E5ECF6')
    fig.update_yaxes(gridcolor='#E5ECF6')

    return fig

if __name__ == '__main__':
    init_forecast_begin()
    dt_time, min_values, max_values = get_max_min(dataSets)
    app.run_server(debug=True)
