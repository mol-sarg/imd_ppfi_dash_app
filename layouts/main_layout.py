# layouts/main_layout.py
from dash import dcc, html, dash_table

# layout constants
NAV_H = "84px"
SIDEBAR_W = "22%"          # keeps percentage width
SIDEBAR_PAD = "18px"       # matches padding
MAIN_PAD_X = "18px"        # horizontal padding for main content
MAIN_PAD_B = "18px"        # bottom padding for main content



layout = html.Div(
    className="app-shell",
    style={
        "minHeight": "100vh",
        "background": "#ffffff",  
        "boxSizing": "border-box",
    },
    children=[
        # navbar
        html.Div(
            className="navbar",
            style={
                "position": "fixed",
                "top": 0,
                "left": 0,
                "right": 0,
                "height": NAV_H,
                "zIndex": 1000,
                "background": "#ffffff",
                "boxSizing": "border-box",
            },
            children=[
                html.Div(
                    [
                        html.Div(
                            "Index of Multiple Deprivation & Priority Places for Food Index: Explorer",
                            className="brand-title",
                        ),
                        html.Div(
                            "Compare vulnerability patterns across England",
                            className="brand-subtitle",
                        ),
                    ]
                )
            ],
        ),

        dcc.Store(id="selected_lad_store", data=None),
        dcc.Store(id="divergence_selected_lsoa", data=None),

        # sidebar
        html.Div(
            className="sidebar",
            style={
                "width": SIDEBAR_W,
                "position": "fixed",
                "top": NAV_H,
                "bottom": 0,
                "left": 0,
                "padding": SIDEBAR_PAD,
                "paddingBottom": "40px",
                "overflowY": "auto",
                "zIndex": 900,
                "boxSizing": "border-box",
                "background": "#ffffff",  # ensures no blue behind sidebar
            },
            children=[
                # view selector
                html.Div(
                    className="sidebar-section",
                    children=[
                        html.Div("View", className="sidebar-label"),
                        dcc.RadioItems(
                            id="view_selector",
                            className="nav-radio",
                            options=[
                                {"label": " About", "value": "about"},
                                {"label": " Map", "value": "map"},
                                {"label": " Side-by-side", "value": "compare"},
                                {"label": " Mismatch explorer", "value": "mismatch"},
                            ],
                            value="about",
                        ),
                    ],
                ),

                # geography selector
                html.Div(
                    id="geography_block",
                    className="sidebar-section",
                    children=[
                        html.Div("Geography", className="sidebar-label"),
                        dcc.RadioItems(
                            id="geography_selector",
                            className="nav-radio",
                            options=[
                                {"label": " Lower Super Output Area (LSOA)", "value": "lsoa"},
                                {"label": " Local Authority District (LAD)", "value": "lad"},
                            ],
                            value="lad",
                        ),
                    ],
                ),

                # dataset selector
                html.Div(
                    id="dataset_block",
                    className="sidebar-section",
                    children=[
                        html.Div("Dataset", className="sidebar-label"),
                        dcc.RadioItems(
                            id="dataset_selector",
                            className="nav-radio",
                            options=[
                                {"label": " PPFI", "value": "ppfi"},
                                {"label": " IMD", "value": "imd"},
                            ],
                            value="ppfi",
                        ),
                    ],
                ),

                # domain selector
                html.Div(
                    id="domain_block",
                    className="sidebar-section",
                    children=[
                        html.Div("Domain", className="sidebar-label"),
                        dcc.Dropdown(
                            id="domain_selector",
                            value="combined",
                            clearable=False,
                        ),
                    ],
                ),

                # lsoa filter
                html.Div(
                    id="lsoa_decile_filter_block",
                    className="sidebar-section",
                    style={"display": "none"},
                    children=[
                        html.Div("LSOA decile filter", className="sidebar-label"),
                        dcc.Dropdown(
                            id="lsoa_decile_filter",
                            options=[{"label": f"Decile {i}", "value": i} for i in range(1, 11)],
                            value=[],
                            multi=True,
                            clearable=True,
                            placeholder="Select one or more deciles",
                        ),
                    ],
                ),

                # LAD percentile filter
                html.Div(
                    id="lad_rank_filter_block",
                    className="sidebar-section",
                    style={"display": "none"},
                    children=[
                        html.Div("LAD rank percentile filter", className="sidebar-label"),
                        dcc.Slider(
                            id="lad_rank_filter",
                            min=0,
                            max=100,
                            step=5,
                            value=100,
                            marks={p: f"{p}%" for p in range(0, 101, 20)},
                        ),
                    ],
                ),

                # compare domains
                html.Div(
                    id="compare_domains_block",
                    className="sidebar-section",
                    style={"display": "none"},
                    children=[
                        html.Div("Compare domains", className="sidebar-label"),
                        html.Div("PPFI Domain", style={"fontWeight": 700, "marginTop": "6px"}),
                        dcc.Dropdown(id="domain_selector_ppfi", value="combined", clearable=False),
                        html.Div("IMD Domain", style={"fontWeight": 700, "marginTop": "12px"}),
                        dcc.Dropdown(id="domain_selector_imd", value="combined", clearable=False),
                    ],
                ),
            ],
        ),

        # main
        html.Div(
            className="main",
            style={
                "marginLeft": SIDEBAR_W,
                "paddingTop": NAV_H,             
                "paddingLeft": MAIN_PAD_X,
                "paddingRight": MAIN_PAD_X,
                "paddingBottom": MAIN_PAD_B,

                "height": f"calc(100vh - {NAV_H})",  
                "display": "flex",
                "flexDirection": "column",
                "minHeight": 0,
                "overflow":"hidden",
                "background": "#ffffff",
                "boxSizing": "border-box",
            },
            children=[

                html.Div(
                    id="map_row",
                    style={
                        "display": "none"},
                    children=[
                        html.Div(
                            id="map_container",
                            style={
                                "flex": 1,
                                "display": "flex",
                                "minHeight": 0,
                                "minWidth": 0,
                                "width": "100%",
                                "boxSizing": "border-box",
                            },
                            children=[
                                dcc.Graph(
                                    id="map_single",
                                    style={
                                        "flex": 1,
                                        "height": "100%",
                                        "width": "100%",
                                        "minHeight": 0,
                                    },
                                    config={"scrollZoom": True},
                                )
                            ],
                        ),
                    ],
                ),

                html.Div(
                    id="compare_panel",
                    className="panel-card",
                    style={
                        "display": "none",     
                        "width": "100%",
                        "maxWidth": "none",
                        "flex": 1,              
                        "minHeight": 0,
                        "boxSizing": "border-box",
                        "padding": "16px",
                    },
                    children=[
                        html.H3("Side-by-side comparison", style={"margin": 0}),
                        html.Div(
                            style={
                                "display": "flex",
                                "gap": "12px",
                                "flex": 1,
                                "height": "100%",
                                "minHeight": 0,
                                "boxSizing": "border-box",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "flex": 1,
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "minHeight": 0,
                                        "minWidth": 0,
                                    },
                                    children=[
                                        html.H4("Priority Places for Food Index", style={"margin": "0 0 6px 0"}),
                                        dcc.Graph(
                                            id="map_compare_left",
                                            style={
                                                "flex": 1,
                                                "height": "100%",
                                                "width": "100%",
                                                "minHeight": 0,
                                            },
                                            config={"scrollZoom": True},
                                        ),
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "flex": 1,
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "minHeight": 0,
                                        "minWidth": 0,
                                    },
                                    children=[
                                        html.H4("Index of Multiple Deprivation", style={"margin": "0 0 6px 0"}),
                                        dcc.Graph(
                                            id="map_compare_right",
                                            style={
                                                "flex": 1,
                                                "height": "125%",
                                                "width": "100%",
                                                "minHeight": 0,
                                            },
                                            config={"scrollZoom": True},
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                # mismatch
                html.Div(
                    id="mismatch_panel",
                    className="panel-card",
                    style={"display": "none",
                           "marginTop": "10px",
                           "flex": 1,
                           "minHeight":0,
                           "overflowY":"auto",
                           "padding":"16px",
                           "boxSizing":"border-box",
                          },
                    children=[
                        html.H3("Mismatch explorer"),
                        # --- filters row ---
                        html.Div(
                            style={"display": "flex", "gap": "12px", "marginBottom": "10px",
                                   "flexWrap": "wrap", "alignItems": "flex-end"},
                            children=[
                                html.Div([
                                    html.Label("Filter by Local Authority:", style={"fontSize": "12px"}),
                                    dcc.Dropdown(
                                        id="mismatch_lad_filter", options=[], value=None,
                                        placeholder="All local authorities",
                                        style={"width": "240px"}, clearable=True,
                                    ),
                                ]),
                                html.Div([
                                    html.Label("Direction:", style={"fontSize": "12px"}),
                                    dcc.Dropdown(
                                        id="mismatch_direction_filter",
                                        options=[
                                            {"label": "All",                 "value": "all"},
                                            {"label": "IMD more deprived",   "value": "high_imd"},
                                            {"label": "PPFI higher priority","value": "high_ppfi"},
                                            {"label": "Broadly aligned",     "value": "aligned"},
                                        ],
                                        value="all", clearable=False,
                                        style={"width": "200px"},
                                    ),
                                ]),
                                html.Div([
                                    html.Label("Min. decile gap:", style={"fontSize": "12px"}),
                                    dcc.Input(
                                        id="mismatch_min_gap", type="number",
                                        min=0, max=9, step=1, value=None,
                                        placeholder="e.g. 3",
                                        style={"width": "80px"},
                                    ),
                                ]),
                            ],
                        ),
                        # --- table ---
                        dash_table.DataTable(
                            id="mismatch_table",
                            columns=[], data=[],
                            page_size=20,
                            sort_action="native",
                            filter_action="native",
                            row_selectable="single",
                            selected_rows=[],
                            style_table={"overflowX": "auto"},
                            style_cell={"fontSize": 12, "padding": "6px"},
                            style_header={"fontWeight": "bold"},
                            style_data_conditional=[
                                {"if": {"filter_query": "{ppfi_imd_diff} > 2"},
                                 "backgroundColor": "#e8f0fb", "color": "#1d3461"},
                                {"if": {"filter_query": "{ppfi_imd_diff} < -2"},
                                 "backgroundColor": "#fdecea", "color": "#7b1e1e"},
                                {"if": {"filter_query": "{abs_diff} >= 5"},
                                 "fontWeight": "bold"},
                            ],
                        ),
                        # --- domain divergence panel (hidden until row selected) ---
                        html.Div(
                            id="domain_divergence_panel",
                            style={"display": "none"},
                            children=[
                                html.Hr(),
                                html.H4(id="domain_divergence_title"),
                                html.Div(id="domain_divergence_narrative"),
                                html.Div(
                                    className="domain-bars-row",
                                    children=[
                                        html.Div(className="domain-bar-col", children=[
                                            html.H5("PPFI domains (decile; 1 = highest priority)"),
                                            dcc.Graph(id="domain_bar_ppfi",
                                                      style={"height": "300px"},
                                                      config={"displayModeBar": False}),
                                        ]),
                                        html.Div(className="domain-bar-col", children=[
                                            html.H5("IMD domains (decile; 1 = most deprived)"),
                                            dcc.Graph(id="domain_bar_imd",
                                                      style={"height": "300px"},
                                                      config={"displayModeBar": False}),
                                        ]),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                #about
                html.Div(
                    id="about_panel",
                    className="panel-card",
                    style={"display": "block", 
                           "marginTop": "10px",
                           "flex":1, 
                           "minHeight":0, 
                           "overflowY":"auto",
                           "padding":"16px",
                           "boxSizing":"border-box",
                          },                    
                    children=[
                        html.H2(
                            "A tool to compare the Index of Multiple Deprivation & Priority Places for Food Index",
                            style={"marginTop": 0, "marginBottom": "4px", "color": "#1a1a2e"},
                        ),
                        html.P("Two maps, two realities \u2014 this tool helps you see where they align and where they don't.",
                               style={"color": "#666", "fontSize": "13px", "marginBottom": "24px"}),
                        html.P(
                            "Across England, living conditions vary widely. The Index of Multiple Deprivation (IMD) "
                            "is the official measure of deprivation across neighbourhoods in England and has historically "
                            "been used to target and evaluate support initiatives, including those relating to food."
                        ),
                        html.P(
                            "However, looking at a map of \u2018deprivation\u2019 doesn\u2019t always show you who is struggling the most. "
                            "Difficulties in accessing healthy, affordable food don\u2019t always affect the most deprived places. "
                            "Two neighbourhoods might look similar on paper yet have completely different everyday realities. "
                            "When we rely only on general deprivation scores to decide where support is needed, we risk "
                            "missing the places \u2014 and the people \u2014 where food access is the real problem."
                        ),
                        html.P("We have created this interactive tool to make these different support needs easier to see.",
                               style={"fontWeight": "600"}),
                        html.Hr(style={"borderColor": "#e0e4f0", "margin": "20px 0"}),
                        html.H4("What the tool brings together", style={"marginBottom": "12px", "color": "#1a1a2e"}),
                        html.P(
                            "This tool brings together two different ways of understanding neighbourhood deprivation "
                            "and need. Each small area receives a score and is ranked from most to least vulnerable, "
                            "with 1 indicating the highest level of vulnerability."
                        ),
                        html.Div(className="info-card info-card--imd", children=[
                            html.H5("Index of Multiple Deprivation (IMD)", style={"margin": "0 0 6px 0", "color": "#1a1a2e"}),
                            html.P([html.Strong("What it measures: "), "Overall disadvantage."], style={"margin": "2px 0"}),
                            html.P([html.Strong("How it works: "),
                                    "It looks at how everyday factors that affect people\u2019s lives \u2014 such as income, "
                                    "employment, housing, health, crime, and access to local services \u2014 combine to "
                                    "create deprivation."], style={"margin": "2px 0"}),
                        ]),
                        html.Div(className="info-card info-card--ppfi", children=[
                            html.H5("Priority Places for Food Index (PPFI)", style={"margin": "0 0 6px 0", "color": "#1a1a2e"}),
                            html.P([html.Strong("What it measures: "), "Access to healthy, affordable food."], style={"margin": "2px 0"}),
                            html.P([html.Strong("How it works: "),
                                    "It considers things like how close shops are, whether the local environment "
                                    "supports access to healthy and affordable foods, and includes factors like "
                                    "income and access to a car."], style={"margin": "2px 0"}),
                        ]),
                        html.Hr(style={"borderColor": "#e0e4f0", "margin": "20px 0"}),
                        html.H4("What you can do with this tool", style={"marginBottom": "12px", "color": "#1a1a2e"}),
                        html.Ul([
                            html.Li("See areas where deprivation and food vulnerability align or diverge."),
                            html.Li("Spot places where food risk appears outside the most deprived areas."),
                            html.Li("Explore patterns across local authorities and across smaller neighbourhoods within those local authorities."),
                        ], style={"lineHeight": "1.9", "paddingLeft": "20px"}),
                        html.Hr(style={"borderColor": "#e0e4f0", "margin": "20px 0"}),
                        html.P(
                            "The tool highlights areas with both high deprivation and poor food access, but it also "
                            "reveals places where these patterns differ \u2014 such as low-deprivation areas with high food "
                            "access risk, or highly deprived areas with good access to shops."
                        ),
                        html.P(
                            "Because users can choose different thresholds for each index (e.g. the top 20% or 40% "
                            "most \u2018vulnerable\u2019), it becomes easy to compare patterns at different levels of need. "
                            "This shows that access to healthy, affordable food is shaped by more than deprivation alone. "
                            "By making these differences easier to see, this tool helps ensure that food-related need "
                            "is clearer and less likely to be overlooked."
                        ),
                        html.P(html.I("Data sources: PPFI V2.1 (Pontin et al. 2024) \u00b7 English IMD 2025 (MHCLG) \u00b7 "
                                      "LSOA 2021 and LAD 2024 boundaries (ONS)."),
                               style={"fontSize": "12px", "color": "#888", "marginTop": "24px"}),
                    ],
                ),
            ],
        ),
    ],
)





