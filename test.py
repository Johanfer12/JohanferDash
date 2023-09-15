import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html

app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'Test'}],
)

layout_dashboard1 = html.Div(
    id="maindiv",
    children=[
        html.Div(children=[
            dcc.Tabs(className='tab-style-sp', id="tabs", colors={'border': '#191B28', 'primary': '#191B28', 'background': '#191B28'}, value='tab-1', children=[
                dcc.Tab(label=' ', value='tab-1', children=[
                        html.Div(style={'width': '90vw'},id="causal_card_graph",children=[
                                dcc.Graph(id='graph1'),
                            ],
                        ),
                    ]),
                dcc.Tab(className='tab-style-xt',label=' ', value='tab-2', children=[html.Label("Test")]),
            ], vertical=True),
        ]),
    ])

server=app.server
app.layout = layout_dashboard1

if __name__ == "__main__":
    app.run_server(debug=True)