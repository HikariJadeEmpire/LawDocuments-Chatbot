import dash, os, base64
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import upload
from pathlib import Path

main_path = Path("main.py").parent
docs_path = Path(main_path,"..","docs_storage")

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
                value=None,
                id="mode",
                labelStyle={"display": "flex", "align-items": "center"},
            ),
            html.Br(), html.Br(),
            html.Small(' Supported documents : ',
                       style={'font-size':11},
                       ), html.Br(),
            html.Small(' .pdf, .csv, .json, .jsonl, .md, .docx, .txt, .html ',
                       style={'font-size':10},
                       ),
            html.Br(), html.Br(),
            dcc.Upload(
                    dbc.Button(
                            " UPLOAD files ", outline=True, color="secondary", className="btn btn-outline-secondary",
                            value = None,
                            style = {'font-size': 16}
                            ),
                    id='docs-load',
                    multiple=True,
                    style = {'textAlign': 'center',}
                ),
            html.Br(),
            html.Div([
                    dbc.DropdownMenu(children=[
                                                html.P(
                                                    "The list of uploaded documents will appear after selecting the MODE.",
                                                    style = {'textAlign': 'center',
                                                            'font-size': 10}
                                                ),
                                            ],
                                        label="Check documents",
                                        # className='nav-item dropdown',
                                        id="docs-list",
                                        size="sm",
                                        toggle_style={
                                                        "background": "#909497",
                                                    },
                                        style = {'textAlign': 'center',},
                                        ),
                    ],
                    style = {'textAlign': 'center',},
                    ),
            html.Br(),
            html.Div(html.Small(children=None,
                                id='docs-load-status'
                                ),
                       style={'font-size':11,
                              'textAlign': 'center',
                              },
                    ),
            html.P(id="doc-dump",
                   style={'font-size':8,
                        'textAlign': 'center',
                        },
                    ),
            html.Br(), html.Br(), html.Br(),
            html.Div([
                        dbc.Button("remove all documents", outline=True, color="danger",
                            className="btn btn-outline-danger btn-sm",
                            id="remove-docs",
                            n_clicks=0,
                            style = {'textAlign': 'center'}
                            ),
                        html.Br(),
                        html.Small(children=None,
                                        id='docs-remove-status'
                                        )
                        ],
                    style={'font-size':11,
                            'textAlign': 'center',
                            },
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
        Output("docs-remove-status","children"),
        Output('remove-docs', 'n_clicks'),

        Input('remove-docs', 'n_clicks'),
)
def remove_docs(click):
    status = None
    doc_check = os.listdir(docs_path)
    if (click >= 1) :
        for  i in doc_check :
            if os.path.exists(docs_path/i):
                os.remove(docs_path/i)

        doc_check = os.listdir(docs_path)
        if (len(doc_check) < 1) :
            click = 0
            status = "All documents has been removed"
            
    elif (click == 0) :
        status = None

    return status, click

@app.callback(
        Output("doc-dump","children"),

        Input('docs-load', 'contents'),
        State('docs-load', 'filename'),
)
def upload_to_dir(docs, name):
    if docs is not None :
        for name, data in zip(name, docs):
            data = data.encode("utf8").split(b";base64,")[1]
            with open(os.path.join(docs_path, name), "wb") as fp:
                fp.write(base64.decodebytes(data))

@app.callback(
    Output("docs-load-status", "children"),
    Output("docs-list","children"),
    [
        Input('mode', 'value'),
        Input('remove-docs', 'n_clicks'),
     ]
)
def upload_status(mode, rm_click):
    
    docs_path.mkdir(parents=True, exist_ok=True)
    doc_check = os.listdir(docs_path)
    
    if (len(doc_check) < 1) or (rm_click >= 1) :
        doc_list = [dbc.DropdownMenuItem('empty',
                                        className="text-body-tertiary",
                                        style = {'textAlign': 'center',
                                                'font-size': 10}
                                        )
                    ]
        status = 'Please upload the documents.'

    elif (len(doc_check) >= 1) and (rm_click == 0) :
        doc_list = []
        for i in doc_check :
            doc_list.append(dbc.DropdownMenuItem(i,
                                        className="text-body-tertiary",
                                        style = {'textAlign': 'center',
                                                'font-size': 10}
                                        )
                            )
        status = 'Your documents has been uploaded'
    
    if mode == 'CWOD' :
        status = None
    return status, doc_list

if __name__ == '__main__':
    app.run(debug=True)