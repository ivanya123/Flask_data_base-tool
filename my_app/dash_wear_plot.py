from dash import Dash, dcc, html, Input, Output, callback, ctx
import plotly.graph_objs as go
import numpy as np


def create_dash_wear(flask_app):
    dash_app = Dash(server=flask_app,
                    url_base_pathname='/dash_wear')

    # dash_app.layout = html.Div(className='