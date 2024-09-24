from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd


def create_dash(flask_app):
    dash_app = Dash(server=flask_app, url_base_pathname='/dash/')

    dash_app.layout = html.Div([
        dcc.Graph(id='graph'),
        dcc.Dropdown(
            id='parameter-dropdown',
            options=[
                {'label': 'Сила резания', 'value': 'cutting_force'},
                {'label': 'Температура резания', 'value': 'cutting_temperature'},
                {'label': 'Стойкость инструмента', 'value': 'tool_life'}
            ],
            value='cutting_force'  # Значение по умолчанию
        )
    ])

    @dash_app.callback(
        Output('graph', 'figure'),
        [Input('parameter-dropdown', 'value')]
    )
    def update_graph(selected_parameter=None):
        graph_data = flask_app.config.get('GRAPH_DATA', {})
        print(graph_data)

        if not graph_data:
            return go.Figure()

        selected_parameter = graph_data.get('selected_parameter', 'cutting_force')

        speed_values = list(range(10, 201, 1))
        Kc = graph_data.get('cutting_force_coefficient', 1)
        Kt = graph_data.get('cutting_temperature_coefficient', 1)
        Kl = graph_data.get('durability_coefficient', 1)
        feed_per_tooth = graph_data.get('feed_per_tooth', 0.1)

        a_force = -0.12
        b_force = 0.95
        a_temp = 0.4
        b_temp = 0.24
        a_life = -0.2
        b_life = -0.15

        if selected_parameter == 'cutting_force':
            values = [Kc * (speed ** a_force) * (feed_per_tooth ** b_force) for speed in speed_values]
        elif selected_parameter == 'cutting_temperature':
            values = [Kt * (speed ** a_temp) * (feed_per_tooth ** b_temp) for speed in speed_values]
        else:
            values = [Kl * (speed ** a_life) * (feed_per_tooth ** b_life) for speed in speed_values]

        fig = go.Figure(data=[go.Scatter(x=speed_values, y=values, mode='lines')])

        selected_speed = graph_data.get('cutting_speed', 10)
        selected_value = next(value for speed, value in zip(speed_values, values) if speed == selected_speed)
        fig.add_trace(
            go.Scatter(x=[selected_speed], y=[selected_value], mode='markers', marker=dict(size=12, color='red'),
                       name='Выбранная точка'))

        fig.update_layout(title=f'График зависимости {selected_parameter} от скорости',
                          xaxis_title='Скорость резания (м/мин)', yaxis_title=selected_parameter)

        return fig

    return dash_app

