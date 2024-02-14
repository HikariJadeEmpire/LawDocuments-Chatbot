import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

app = Dash(
    title='DocsChat',
    name='DocsChat',
    update_title='Updating..',
    use_pages=False,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.YETI]
)

app.layout = dbc.Container([
    dbc.Row([
        
        ### HEADER ###

        dbc.Col([
            html.Br(), html.Br(),
            html.Div(children=[html.H3(' 📚 Chat! '),
                               html.Small(' with your DOCUMENTS '),
                               html.Br(), html.Br(),
                            dbc.Badge("by SATURDAY",
                                     color='rgb(142, 68, 173)',
                                    #  text_color="warning" ,
                                     className="badge bg-secondary", 
                                     id="model-name")
                                     ], 
                            style = {'height':'200px','textAlign': 'left',}
                            ),
            html.Br(), html.Br(),
            html.H6(' MODE '),
            dcc.RadioItems(
                [
                    {
                        "label":
                            [
                                # html.Img(src="/assets/images/language_icons/python_50px.svg", height=30),
                                html.Span("Chat with documents", style={'font-size': 13, 'padding-left': 10}),
                            ],
                        "value": "CWD",
                    },
                    {
                        "label":
                            [
                                # html.Img(src="/assets/images/language_icons/julia_50px.svg", height=30),
                                html.Span("Search for documents", style={'font-size': 13, 'padding-left': 10}),
                            ], 
                        "value": "SD",
                    },
                    {
                        "label":
                            [
                                # html.Img(src="/assets/images/language_icons/r-lang_50px.svg", height=30),
                                html.Span("Chat without documents", style={'font-size': 13, 'padding-left': 10}),
                            ],
                        "value": "CWOD",
                    },
                ],
                value="CWD",
                id="mode",
                labelStyle={"display": "flex", "align-items": "center"},
            ),
            html.Br(), html.Br(),
            dcc.Upload(
                dbc.Button(
                " UPLOAD files ", outline=True, color="secondary", className="btn btn-outline-secondary",
                style = {'font-size': 16}
                ), style = {'textAlign': 'center',}
            ),

            ], 
            width = 2 ,
            style={
                'margin': '10px',
                'border-radius': '0px',
                # 'background-color':'rgb(151, 154, 154)',
                }
            ),

        ### CHAT AREA ###

        dbc.Col([

            ],
            width = 9 ,
            style={
            'margin': '10px',
            'border-radius': '0px',
            # 'background-color':'rgb(151, 154, 154)',
            }
            ),
    ]),

    # END

    ])

@app.callback(
    Output("graph", "figure"), 
    [
        Input('interval', 'max_intervals'), 
        Input('storage-df', 'data'),
        Input("choice0", "value"),
     ]
)
def plot_graph(max_intervals, df, coin):
    pass

if __name__ == '__main__':
    app.run(debug=True)