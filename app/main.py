import dash, os, base64, time
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from dotenv import load_dotenv, find_dotenv
from pathlib import Path

import requests

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
        html.Br(),
        html.Div([
            html.Small("CHATBOT STATUS",
                       style = {'textAlign': 'center',
                                'font-size': 10},
                                ),
            dbc.Spinner(
                html.P("The chatbot currently doesn't have information from documents yet.",
                   className="text-info",
                   style={
                       'textAlign': 'center',
                        'font-size': 10
                   },
                   ),
                id="status",
                ),
                ],
                 style = {'textAlign': 'center',}
                 ),
        html.Br(),
            ],
            style={
            'margin': '10px',
            'border-radius': '0px',
            # 'background-color':'rgb(151, 154, 154)',
            }),

    dbc.Row([
        
        ### HEADER ###

        dbc.Col([
            html.Div(children=[html.H3(' 📚 Chat! '),
                               html.Small(' with your DOCUMENTS '),
                               html.Br(), html.Br(),
                            dbc.Badge("by SATURDAY",
                                     color='rgb(142, 68, 173)',
                                    #  text_color="warning" ,
                                     className="badge bg-secondary", 
                                     id="model-name")
                                     ], 
                            style = {'height':'180px','textAlign': 'left',}
                            ),
            html.Br(),
            html.Div([
                dbc.Input(  type="password",
                            id="huggingface-api",
                            valid=True,
                            size="sm",
                            className="form-control is-invalid",
                            placeholder="Your Huggingface API",
                        ),
                html.Small('You can access the Hugging Face API (READ) from this link (Don\'t worry, it\'s FREE)',
                           style = {
                                'font-size': 8
                                }
                           ),
                dcc.Link(   children="Access tokens",
                            href="https://huggingface.co/settings/tokens",
                            className="btn btn-link",
                            refresh=True,
                            style = {
                                'font-size': 9
                                }
                            ),
                html.Br(),
                    ]
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
                                        color="secondary",
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
            dcc.Store(id="huggingface-api-store"),
            dcc.Store(id="doc-dump"),
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
                dbc.Row([
                    dbc.Nav(
                            [
                                dbc.NavLink("Models info",
                                            id="open-model-details",
                                            active=True,
                                            href="#",
                                            n_clicks=0,
                                            className="nav-link",
                                            ),
                            ]
                        ),
                    dbc.Popover(
                                [
                                    dbc.PopoverHeader("Popover header"),
                                    dbc.PopoverBody("And here's some amazing content. Cool!"),
                                ],
                                id="popover",
                                is_open=False,
                                placement="right",
                                target="open-model-details",
                            ),
                    html.Br(),
                ],
                ),
                dbc.Row([
                    html.Div([
                        "Chat area"
                    ])
                ],
                style = {
                    "maxHeight":"400px",
                    "overflow": "scroll"
                    },
                ),
                dbc.Row([
                    html.Div([
                        "Typing area"
                    ])
                ]
                ),
            ],
            width = 9 ,
            style={
            'margin': '10px',
            'border-radius': '0px',
            # 'background-color':'rgb(151, 154, 154)',
            }
            ),
    ]),

    ### CHAT AREA END ###

    dbc.Row([
        html.Br(), html.Br(),
        html.Div([
            html.Small("By HikariJadeEmpire",
                       style = {'textAlign': 'center',
                                'font-size': 10},
                                ),
                ],
                 style = {'textAlign': 'center',}
                 ),
        html.Br(), html.Br(),
    ],

    ),

    # END

    ])

@app.callback(
    Output("popover", "is_open"),
    [Input("open-model-details", "n_clicks")],
    [State("popover", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
        Output("huggingface-api","className"),
        Output("huggingface-api-store","data"),

        Input("huggingface-api", "value"),

)
def huggingface_api_check(huggingface_api):
    checked = "form-control is-invalid"

    url = 'https://huggingface.co/api/whoami-v2'
    headers = {'Authorization': "Bearer {token}".format(token=huggingface_api)}
    r = requests.get(url, headers=headers)

    if r.status_code == 200 :
        checked = "form-control is-valid"
        api_passed = huggingface_api
    else :
        api_passed = "x"

    return checked, api_passed

@app.callback(
        Output("status","children"),

        Input("docs-load-status", "children"),
)
def chatbot_status_update(doc_status):
    doc_check = os.listdir(docs_path)
    if doc_status == "Your documents has been uploaded":
        if (len(doc_check) >= 1):
            text = html.P("The chatbot has already obtained the information from the documents.",
                   className="text-success",
                   style={
                       'textAlign': 'center',
                        'font-size': 10
                   },
                   )
        else :
            text = html.P("[ RECEIVING DOCUMENTS ERROR ] : It seems like your documents haven't been collected.",
                    className="text-danger",
                            style={
                                'textAlign': 'center',
                                    'font-size': 10
                            },
                            )
        return text
    
    elif doc_status == "Please upload the documents.":
        if (len(doc_check) < 1):
            text = html.P("The chatbot currently doesn't have information from documents yet.",
                   className="text-info",
                   style={
                       'textAlign': 'center',
                        'font-size': 10
                   },
                   )
        else :
            text = html.P("[ RECEIVING DOCUMENTS ERROR ] : It seems like your documents have been collected.",
                          className="text-danger",
                            style={
                                'textAlign': 'center',
                                    'font-size': 10
                            },
                          )
        return text
    else :
        return dash.no_update

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
            print("All documents successfully removed.")
        click = 0

    return status, click

@app.callback(
        Output("doc-dump","data"),

        Input('docs-load', 'contents'),
        State('docs-load', 'filename'),
)
def upload_to_dir(docs, name):
    if docs is not None :
        for name, data in zip(name, docs):
            data = data.encode("utf8").split(b";base64,")[1]
            with open(os.path.join(docs_path, name), "wb") as fp:
                fp.write(base64.decodebytes(data))
        return "uploaded"

@app.callback(
    Output("docs-load-status", "children"),
    Output("docs-list","children"),
    [
        Input('mode', 'value'),
        Input('remove-docs', 'n_clicks'),
        Input("doc-dump","data"),
     ]
)
def upload_status(mode, rm_click, doc_uploaded):
    
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

    elif (len(doc_check) >= 1) and (rm_click == 0) or (doc_uploaded == "uploaded") :
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