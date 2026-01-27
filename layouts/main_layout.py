
# layouts/main_layout.py
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

layout = html.Div(
    className='app-shell',
    children=[

        # nav bar
        html.Div(
            className='navbar',
            children=[
                html.Div(
                    [
                        html.Div(
                            'Index of Multiple Deprivation & Priority Places for Food Index: Explorer',
                            className='brand-title',
                        ),
                        html.Div(
                            'Compare vulnerability patterns across England',
                            className='brand-subtitle',
                        ),
                    ]
                )
            ],
        ),

        # side bar
        html.Div(
            className='sidebar',
            style={
                'width': '22%',
                'position': 'fixed',
                'top': '96px',
                'bottom': 0,
                'padding': '18px',
                'paddingBottom': '40px',
                'overflowY': 'auto',
            },
            children=[

                # view selector
                html.Div(
                    className='sidebar-section',
                    children=[
                        html.Div('View', className='sidebar-label'),
                        dcc.RadioItems(
                            id='view_selector',
                            className='nav-radio',
                            options=[
                                {'label': ' Map', 'value': 'map'},
                                {'label': ' Side-by-side', 'value': 'compare'},
                                {'label': ' Summary statistics', 'value': 'stats'},
                                {'label': ' Mismatch explorer', 'value': 'mismatch'},
                                {'label': ' About', 'value': 'about'},
                            ],
                            value='map',
                        ),
                    ],
                ),

                # geog selector
                html.Div(
                    id='geography_block', 
                    className='sidebar-section',
                    children=[
                        html.Div('Geography', className='sidebar-label'),
                        dcc.RadioItems(
                            id='geography_selector',
                            className='nav-radio',
                            options=[
                                {'label': ' Lower Super Output Area (LSOA)', 'value': 'lsoa'},
                                {'label': ' Local Authority District (LAD)', 'value': 'lad'},
                            ],
                            value='lad',
                        ),
                    ],
                ),

                # data selector
                html.Div(
                    id='dataset_block',
                    className='sidebar-section',
                    children=[
                        html.Div('Dataset', className='sidebar-label'),
                        dcc.RadioItems(
                            id='dataset_selector',
                            className='nav-radio',
                            options=[
                                {'label': ' PPFI', 'value': 'ppfi'},
                                {'label': ' IMD', 'value': 'imd'},
                            ],
                            value='ppfi',
                        ),
                    ],
                ),

                # domain selector
                html.Div(
                    id='domain_block',
                    className='sidebar-section',
                    children=[
                        html.Div('Domain', className='sidebar-label'),
                        dcc.Dropdown(
                            id='domain_selector',
                            value='combined',
                            clearable=False,
                        ),
                    ],
                ),

                # lsoa filter
                html.Div(
                    id='lsoa_decile_filter_block',
                    className='sidebar-section',
                    style={'display': 'none'},
                    children=[
                        html.Div('LSOA decile filter', className='sidebar-label'),
                        dcc.Dropdown(
                            id='lsoa_decile_filter',
                            options=[{'label': f'Decile {i}', 'value': i} for i in range(1, 11)],
                            value=[],
                            multi = True,
                            clearable=True,
                            placeholder='Select one or more deciles',
                        ),
                    ],
                ),

                # LAD percentile filter
                html.Div(
                    id='lad_rank_filter_block',
                    className='sidebar-section',
                    style={'display': 'none'},
                    children=[
                        html.Div('LAD rank percentile filter', className='sidebar-label'),
                        dcc.Slider(
                            id='lad_rank_filter',
                            min=0,
                            max=100,
                            step=5,
                            value=100,
                            marks={p: f'{p}%' for p in range(0, 101, 20)},
                        ),
                    ],
                ),

                # compare domains
                html.Div(
                    id='compare_domains_block',
                    className='sidebar-section',
                    style={'display': 'none'},
                    children=[
                        html.Div('Compare domains', className='sidebar-label'),
                        html.Div('PPFI Domain', style={'fontWeight': 700, 'marginTop': '6px'}),
                        dcc.Dropdown(id='domain_selector_ppfi', value='combined', clearable=False),
                        html.Div('IMD Domain', style={'fontWeight': 700, 'marginTop': '12px'}),
                        dcc.Dropdown(id='domain_selector_imd', value='combined', clearable=False),
                    ],
                ),
            ],
        ),

        # main content
        html.Div(
            className='main',
            style={
                'marginLeft': '24%',
                'padding': '96px 0 0 0',
                'overflow': 'visible',
            },
            children=[

                # map row
                html.Div(
                    id='map_row',
                    style={
                        'display': 'flex',
                        'flexDirection': 'row',
                        'width': '100%',
                    },
                    children=[
                        html.Div(
                            id='map_container',
                            style={
                                'flex': '1',
                                'height': '90vh',
                                'position': 'relative',
                            },
                            children=[
                                dcc.Graph(
                                    id='map_single',
                                    style={'height': '100%', 'width': '100%'},
                                    config={'scrollZoom': True},
                                )
                            ],
                        ),
                    ],
                ),

                # side by side view
                html.Div(
                    id='compare_panel',
                    className='panel-card',
                    style={'display': 'none', 'marginTop': '10px'},
                    children=[
                        html.H3('Side-by-side comparison'),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4('PPFI'),
                                        dcc.Graph(
                                            id='map_compare_left',
                                            style={'height': '90vh'},
                                            config={'scrollZoom': True},
                                        ),
                                    ],
                                    style={'width': '49%', 'display': 'inline-block'},
                                ),
                                html.Div(
                                    [
                                        html.H4('IMD'),
                                        dcc.Graph(
                                            id='map_compare_right',
                                            style={'height': '90vh'},
                                            config={'scrollZoom': True},
                                        ),
                                    ],
                                    style={'width': '49%', 'display': 'inline-block', 'float': 'right'},
                                ),
                            ]
                        ),
                    ],
                ),

                # stats panel
                html.Div(
                    id='stats_panel',
                    className='panel-card',
                    style={'display': 'none', 'marginTop': '10px'},
                    children=[html.H3('Summary statistics'), html.Div(id='stats_content')],
                ),

                # mismatch panel
                html.Div(
                    id='mismatch_panel',
                    className='panel-card',
                    style={'display': 'none', 'marginTop': '10px'},
                    children=[
                        html.H3('Mismatch explorer'),
                        html.Label('Filter by Local Authority:'),
                        dcc.Dropdown(
                            id='mismatch_lad_filter',
                            options=[],
                            value=None,
                            placeholder='All local authorities',
                            style={'width': '60%'},
                            clearable=True,
                        ),
                        dash_table.DataTable(
                            id='mismatch_table',
                            columns=[],
                            data=[],
                            page_size=20,
                            sort_action='native',
                            filter_action='native',
                            style_table={'overflowX': 'auto'},
                            style_cell={'fontSize': 12, 'padding': '6px'},
                            style_header={'fontWeight': 'bold'},
                        ),
                    ],
                ),

                # about panel - finish
                html.Div(
                    id='about_panel',
                    className='panel-card',
                    style={'display': 'none', 'marginTop': '10px'},
                    children=[
                        html.H3('ABOUT'),
                        html.P(
                            'This tool helps policymakers compare IMD and PPFI, showing where they align and differ.'
                        ),
                    ],
                ),
            ],
        ),
    ],
)
