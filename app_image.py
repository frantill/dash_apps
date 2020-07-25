import datetime
import collections
import dash
import pandas as pd

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

# This stylesheet makes the buttons and table pretty.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")


app.layout = html.Div([
    html.H1(children='Ottimo'),
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    # dcc.Graph(
    #     id='example-graph',
    #     figure=fig
    # ),
    html.Div(id='output-image-upload'),
    dcc.Tabs([
        dcc.Tab(label='Tab one', children=[    #### TAB 1
            # The memory store reverts to the default on every page refresh
            dcc.Store(id='memory'),
            # The local store will take the initial data
            # only the first time the page is loaded
            # and keep it until it is cleared.
            dcc.Store(id='local', storage_type='local'),
            # Same as the local store but will lose the data
            # when the browser/tab closes.
            dcc.Store(id='session', storage_type='session'),
            html.Table([
                html.Thead([
                    html.Tr(html.Th('Click to store in:', colSpan="3")),
                    html.Tr([
                        html.Th(html.Button('memory', id='memory-button')),
                        html.Th(html.Button('localStorage', id='local-button')),
                        html.Th(html.Button('sessionStorage', id='session-button'))
                    ]),
                    html.Tr([
                        html.Th('Memory clicks'),
                        html.Th('Local clicks'),
                        html.Th('Session clicks')
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(0, id='memory-clicks'),
                        html.Td(0, id='local-clicks'),
                        html.Td(0, id='session-clicks')
                    ])
                ])
            ])

            # dcc.Graph(
            #     figure={
            #         'data': [
            #             {'x': [1, 2, 3], 'y': [4, 1, 2],
            #                 'type': 'bar', 'name': 'SF'},
            #             {'x': [1, 2, 3], 'y': [2, 4, 5],
            #              'type': 'bar', 'name': u'Montréal'},
            #         ]
            #     }
            # )
        ]),
        dcc.Tab(label='Tab two', children=[    #### TAB 2
            dcc.Upload(
                    id='upload-image_TAB2',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
            dcc.Graph(
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [1, 4, 1],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [1, 2, 3],
                         'type': 'bar', 'name': u'Montréal'},
                    ]
                }
            ),
        ]),
        dcc.Tab(label='Tab three', children=[    #### TAB 3
            dcc.Graph(
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [2, 4, 3],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [5, 4, 3],
                         'type': 'bar', 'name': u'Montréal'},
                    ]
                }
            )
        ]),
    ])
])


def parse_contents(contents, filename, date):
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


# Create two callback for every store.
for store in ('memory', 'local', 'session'):

    # add a click to the appropriate store.
    @app.callback(Output(store, 'data'),
                  [Input('{}-button'.format(store), 'n_clicks')],
                  [State(store, 'data')])
    def on_click(n_clicks, data):
        if n_clicks is None:
            # prevent the None callbacks is important with the store component.
            # you don't want to update the store for nothing.
            raise PreventUpdate

        # Give a default data dict with 0 clicks if there's no data.
        data = data or {'clicks': 0}

        data['clicks'] = data['clicks'] + 1
        return data

    # output the stored clicks in the table cell.
    @app.callback(Output('{}-clicks'.format(store), 'children'),
                  # Since we use the data prop in an output,
                  # we cannot get the initial data on load with the data prop.
                  # To counter this, you can use the modified_timestamp
                  # as Input and the data as State.
                  # This limitation is due to the initial None callbacks
                  # https://github.com/plotly/dash-renderer/pull/81
                  [Input(store, 'modified_timestamp')],
                  [State(store, 'data')])
    def on_data(ts, data):
        if ts is None:
            raise PreventUpdate

        data = data or {}

        return data.get('clicks', 0)

@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')],
              [State('upload-image', 'filename'),
               State('upload-image', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)