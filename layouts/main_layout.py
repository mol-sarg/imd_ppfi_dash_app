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
                                {"label": " Map", "value": "map"},
                                {"label": " Side-by-side", "value": "compare"},
                                {"label": " Summary statistics", "value": "stats"},
                                {"label": " Mismatch explorer", "value": "mismatch"},
                                {"label": " About", "value": "about"},
                            ],
                            value="map",
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

                "background": "#ffffff",
                "boxSizing": "border-box",
            },
            children=[

                html.Div(
                    id="map_row",
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "width": "100%",
                        "flex": 1,        
                        "minHeight": 0,   
                        "maxHeight": "none",
                        "boxSizing": "border-box",
                    },
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
                                        html.H4("PPFI", style={"margin": "0 0 6px 0"}),
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
                                        html.H4("IMD", style={"margin": "0 0 6px 0"}),
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

                # stats
                html.Div(
                    id="stats_panel",
                    className="panel-card",
                    style={"display": "none", "marginTop": "10px"},
                    children=[
                        html.H3("Summary statistics"),
                        html.Div(id="stats_content"),
                    ],
                ),

                # mismatch
                html.Div(
                    id="mismatch_panel",
                    className="panel-card",
                    style={"display": "none", "marginTop": "10px"},
                    children=[
                        html.H3("Mismatch explorer"),
                        html.Label("Filter by Local Authority:"),
                        dcc.Dropdown(
                            id="mismatch_lad_filter",
                            options=[],
                            value=None,
                            placeholder="All local authorities",
                            style={"width": "60%"},
                            clearable=True,
                        ),
                        dash_table.DataTable(
                            id="mismatch_table",
                            columns=[],
                            data=[],
                            page_size=20,
                            sort_action="native",
                            filter_action="native",
                            style_table={"overflowX": "auto"},
                            style_cell={"fontSize": 12, "padding": "6px"},
                            style_header={"fontWeight": "bold"},
                        ),
                    ],
                ),

                #about
                html.Div(
                    id="about_panel",
                    className="panel-card",
                    style={"display": "none", "marginTop": "10px"},
                    children=[
                        html.H3("ABOUT"),
                        html.P("This tool helps policymakers compare IMD and PPFI, showing where they align and differ."),
                    ],
                ),
            ],
        ),
    ],
)
