import dash, os, base64
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from dotenv import load_dotenv, find_dotenv
from pathlib import Path

import requests
import timeit

import m_vector_db

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
                    style={
                            'font-size':11,
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
                    html.Div([
                        dbc.Nav(
                            [
                                dbc.NavLink("Fresh start",
                                            id="app-details",
                                            active=True,
                                            href="#",
                                            n_clicks=0,
                                            className="nav-link",
                                            ),
                                dbc.NavLink("Huggingface API",
                                            id="open-hug",
                                            active=True,
                                            href="#",
                                            n_clicks=0,
                                            className="nav-link",
                                            ),
                                dbc.NavLink("LLM info",
                                            id="open-llm-details",
                                            active=True,
                                            href="#",
                                            n_clicks=0,
                                            className="nav-link",
                                            ),
                                dbc.NavLink("Embedding model info",
                                            id="open-model-details",
                                            active=True,
                                            href="#",
                                            n_clicks=0,
                                            className="nav-link",
                                            ),
                            ],
                            style={
                                'font-size':12,
                                'textAlign': 'center',
                            },
                            class_name="nav nav-tabs",
                        )
                        ],
                        style={
                            'textAlign':'center',
                        },
                    ),
                    dbc.Popover(
                                [
                                    dbc.PopoverHeader("First opening"),
                                    dbc.PopoverBody("You may experience slow document retrieval,"),
                                    dbc.PopoverBody(
                                        "especially the first time you use the application, due to model downloads.",
                                         style={'font-size':12},
                                                    ),
                                ],
                                id="popover-start",
                                is_open=False,
                                placement="right",
                                target="app-details",
                            ),
                    dbc.Popover(
                                [
                                    dbc.PopoverHeader("Embeddings"),
                                    dbc.PopoverBody("sentence-transformers/paraphrase-multilingual-mpnet-base-v2"),
                                    dbc.PopoverBody(
                                        "model is utilized for document retrieval purposes.",
                                        style={'font-size':12},
                                                    ),
                                ],
                                id="popover",
                                is_open=False,
                                placement="right",
                                target="open-model-details",
                            ),
                    dbc.Popover(
                                [
                                    dbc.PopoverHeader("Large Language Model (LLM)"),
                                    dbc.PopoverBody("..."),
                                ],
                                id="popover-llm",
                                is_open=False,
                                placement="right",
                                target="open-llm-details",
                            ),
                    dbc.Popover(
                                [
                                    dbc.PopoverHeader("Huggingface API"),
                                    dbc.PopoverBody(
                                        'You can access the Hugging Face API (Role : READ) from the link below (Don\'t worry, it\'s FREE)',
                                        style = {
                                                'font-size': 12
                                                }
                                                 ),
                                    dbc.PopoverBody(
                                        dcc.Link(   
                                            children="Access tokens",
                                            href="https://huggingface.co/settings/tokens",
                                            className="btn btn-link",
                                            refresh=True,
                                            style = {
                                                'font-size': 12
                                                }
                                            )
                                        ),
                                ],
                                id="popover-huggingface",
                                is_open=False,
                                placement="right",
                                target="open-hug",
                            ),
                    html.Br(),
                ],
                align='center',
                ),

            ##### STACK MESSAGE #####

                dbc.Row([
                    html.H5(""),
                    dcc.Store(id="chat-stack"),
                    dcc.Store(id="current-table-name"),
                    dbc.ListGroup(children=[
                            dbc.ListGroupItem([
                                html.Div("SATURDAY", className="badge rounded-pill bg-success"),
                                html.P("Hi, how can I assist you today ?"),
                            ],
                            style={
                                'textAlign':'left',
                                'font-size':15,
                                'border-top-left-radius':'10px',
                                'border-top-right-radius':'10px',
                                'border-bottom-right-radius':'10px',
                                },
                                    ),
                            dbc.ListGroupItem([
                                html.Div("USER", className="badge rounded-pill bg-info"),
                                html.P("Whatever")
                            ],
                            style={
                                'textAlign':'right',
                                'font-size':15,
                                'border-top-left-radius':'10px',
                                'border-top-right-radius':'10px',
                                'border-bottom-left-radius':'10px',
                                }
                            ),
                        ],
                        id="chatbox"
                        ),
                    ],
                    style = {
                        'height':'650px',
                        "maxHeight":"650px",
                        "overflow": "scroll"
                        },
                ),
                dbc.Row([
                    html.Br(),
                    html.Div([
                        dbc.Spinner(
                                    html.P(
                                        "Time to chat",
                                        style={'font-size':11}
                                           ),
                                    size="sm",
                                    id="chat-status"
                                    ),
                        dbc.InputGroup([
                            dbc.Button(
                                        "clear messages", outline=True, color="secondary",
                                        id="ms-clear",
                                        n_clicks=0,
                                        style={
                                            'font-size':12,
                                        },
                                    ),
                            dbc.Textarea(
                                        placeholder="Your input...",
                                        className="form-control",
                                        id="ms-type",
                                        style={
                                            'font-size':12,
                                        },
                                    ),
                            dbc.Button(
                                        "SEND", outline=True, color="secondary",
                                        id="ms-sent",
                                        n_clicks=0,
                                    )
                                ]),
                        dbc.FormText("Type something in the box above", style={'font-size':10}),
                    ],
                    style = {'textAlign': 'center',}
                    ),
                    html.Br(),
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
        html.Br(),
        html.H1(""),
        html.Div([
            html.Small("By HikariJadeEmpire",
                       style = {
                           'textAlign': 'center',
                            'font-size': 10,
                                },
                        ),
                ],
                 style = {
                     'height':'100px',
                     'textAlign': 'center',
                     }
                 ),
        html.Br(), html.Br(),
    ],

    ),

    # END

    ])

@app.callback(
    Output("popover-start", "is_open"),
    [Input("app-details", "n_clicks")],
    [State("popover-start", "is_open")],
)
def toggle_popover_fresh_start(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("popover-huggingface", "is_open"),
    [Input("open-hug", "n_clicks")],
    [State("popover-huggingface", "is_open")],
)
def toggle_popover_huggingface(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("popover", "is_open"),
    [Input("open-model-details", "n_clicks")],
    [State("popover", "is_open")],
)
def toggle_popover_embedding(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("popover-llm", "is_open"),
    [Input("open-llm-details", "n_clicks")],
    [State("popover-llm", "is_open")],
)
def toggle_popover_llm(n, is_open):
    if n:
        return not is_open
    return is_open

########################################################

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
        Output("current-table-name","data"),

        Input("docs-load-status", "children"),
        Input("huggingface-api-store","data"),
        Input("current-table-name","data"),
)
def chatbot_status_update(doc_status, huggingface_valid, table_name):
    doc_check = os.listdir(docs_path)
    t_name = [f"Table-{i}" for i in range(999)]
    if doc_status == "Your documents has been uploaded":
        if (len(doc_check) >= 1) and (huggingface_valid != 'x'):

            mydb = m_vector_db.vectordb_start(huggingface_api_key=huggingface_valid)

            try :
                mydb.add(table_name=t_name[0])
            except :
                t_name.pop(0)
                mydb.add(table_name=t_name[0])

            text = html.P("The chatbot has already obtained the information from the documents.",
                   className="text-success",
                   style={
                       'textAlign': 'center',
                        'font-size': 10
                   },
                   )
        else :
            text = html.P("[ RECEIVING DOCUMENTS ERROR ] : It seems like your documents haven't been collected. Please check your huggingface API",
                    className="text-danger",
                            style={
                                'textAlign': 'center',
                                    'font-size': 10
                            },
                            )
            
        return text, t_name[0]
    
    elif doc_status == "Please upload the documents.":
        if (len(doc_check) < 1) and (huggingface_valid == 'x'):
            text = html.P("The chatbot currently doesn't have information from documents yet. Please check your huggingface API",
                   className="text-info",
                   style={
                       'textAlign': 'center',
                        'font-size': 10
                   },
                   )
        elif (len(doc_check) < 1) and (huggingface_valid != 'x'):
            mydb = m_vector_db.vectordb_start(huggingface_api_key=huggingface_valid)
            try :
                if table_name is not None :
                    mydb.remove_db(table_name=table_name)
            except :
                pass
            
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
        return text, dash.no_update
    
    else :
        return dash.no_update, dash.no_update

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

###############################################

@app.callback(
    Output("chat-stack", "data"),
    Output("chat-status", "children"),
    [
        Input('mode', 'value'),
        Input('ms-type', 'value'),
        Input('ms-sent', 'n_clicks'),
        Input('ms-clear', 'n_clicks'),
        Input("huggingface-api-store","data"),
        Input("current-table-name","data"),
        Input("status","children"),
     ]
)
def chatbox(mode, message, confirm_message, clear_message, huggingface_valid, table_name, chatbot_status):

    stacks = {'user':[], 'chatbot':[], 'time':[], 'distance':[], 'ref':[]}

    if confirm_message and (message is not None) :
        if (huggingface_valid != 'x') and (chatbot_status == "The chatbot has already obtained the information from the documents.") :
            mydb = m_vector_db.vectordb_start(huggingface_api_key=huggingface_valid)
            if mode == 'SD':

                start_time = timeit.default_timer()
                results = mydb.retrieve(query=message, table_name=table_name)
                time = timeit.default_timer() - start_time

                answer = "XXX"
                ref = (results['documents'][0])[0]
                distance = (results['distances'][0])[0]

            elif mode == 'CWD':
                pass
            elif mode == 'CWOD':
                pass
        elif (huggingface_valid == 'x') or (chatbot_status != "The chatbot has already obtained the information from the documents.") :
            if mode == 'CWOD':
                pass
            else :
                ## cannot response without api and table name
                answer = "Please ensure that you have correctly filled in the Hugging Face API and uploaded the documents."
                ref = "XXX"
                distance = "XXX"
                time = "XXX"
        
        stacks['user'].append(message)
        stacks['chatbot'].append(answer)
        stacks['time'].append(time)
        stacks['distance'].append(distance)
        stacks['ref'].append(ref)

        ms_process = html.P(
                            "number of questions : {A}".format(A=len(stacks.items())),
                            style={'font-size':11}
                                )
        return stacks, ms_process
    
    elif clear_message :
        stacks = dict()
        ms_process = html.P(
                            "number of questions : {A}".format(A=len(stacks.items())),
                            style={'font-size':11}
                                )
        return stacks, ms_process
    else :
        return dash.no_update, dash.no_update

@app.callback(
    Output("chatbox", "children"),
    [
        Input("chat-stack", "data"),
        Input('mode', 'value'),
        Input('ms-sent', 'n_clicks'),
    ]
    )
def update_chatbox(stacks, mode, sent_ms):
    docr = ["CWD","SD"]

    final_stacks = []

    if sent_ms :
        for user,chatbot,time,distance,ref in zip(stacks['user'],stacks['chatbot'],stacks['time'],stacks['distance'],stacks['ref']):

            chatbot_area = [html.Div("SATURDAY", className="badge rounded-pill bg-success")]
            user_area = [html.Div("USER", className="badge rounded-pill bg-info")]

            if mode == "SD":
                for i in ref.split("\n"):
                    chatbot_area.append(html.P(i))
                chatbot_area.extend([
                            html.Div("INFO", className="badge rounded-pill bg-light"),
                            html.P(f"DISTANCE : {distance}"),
                            html.P(f"RETRIEVAL TIME : {time}")
                            ])
            elif mode == "CWD":
                for i in chatbot.split("\n"):
                    chatbot_area.append(html.P(i))
                chatbot_area.extend([
                            html.Div("INFO", className="badge rounded-pill bg-light"),
                            html.P(f"REFERENCE : {ref}"),
                            html.P(f"RETRIEVAL TIME : {time}")
                            ])
            elif mode not in docr :
                for i in chatbot.split("\n"):
                    chatbot_area.append(html.P(i))
                chatbot_area.extend([
                            html.Div("INFO", className="badge rounded-pill bg-light"),
                            html.P(f"TIME : {time}")
                            ])
                
            for i in user.split("\n"):
                user_area.append(html.P(i))

            stack_chat = [
                            dbc.ListGroupItem(
                                chatbot_area,
                                style={
                                    'textAlign':'left',
                                    'font-size':15,
                                    'border-top-left-radius':'10px',
                                    'border-top-right-radius':'10px',
                                    'border-bottom-right-radius':'10px',
                                    },
                                    ),
                            dbc.ListGroupItem(
                                user_area,
                                style={
                                    'textAlign':'right',
                                    'font-size':15,
                                    'border-top-left-radius':'10px',
                                    'border-top-right-radius':'10px',
                                    'border-bottom-left-radius':'10px',
                                    }
                                    ),
                        ]
            final_stacks.extend(stack_chat)
        return final_stacks
    else :
        return dash.no_update

if __name__ == '__main__':
    app.run(debug=True)