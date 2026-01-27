
# callbacks/navigation_callbacks.py
from dash.dependencies import Input, Output
from app import app


@app.callback(
    Output('map_row', 'style'),
    Output('compare_panel', 'style'),
    Output('stats_panel', 'style'),
    Output('mismatch_panel', 'style'),
    Output('about_panel', 'style'),

    Output('geography_block', 'style'),  # 👈 NEW

    Output('dataset_block', 'style'),
    Output('domain_block', 'style'),
    Output('compare_domains_block', 'style'),
    Output('lsoa_decile_filter_block', 'style'),
    Output('lad_rank_filter_block', 'style'),
    Input('view_selector', 'value'),
    Input('geography_selector', 'value'),
)
def switch_view(view, geo):
    show_map_row = {'display': 'flex', 'flexDirection': 'row', 'width': '100%'}
    hide_map_row = {'display': 'none'}

    show_panel = {'display': 'block', 'marginTop': '10px'}
    hide_panel = {'display': 'none'}

    show = {'display': 'block'}
    hide = {'display': 'none'}
    geography_style = show if view in ['map', 'compare'] else hide
    # filters only relevant for map/compare
    lsoa_filter = show if geo == 'lsoa' and view in ['map', 'compare'] else hide
    lad_filter = show if geo == 'lad' and view in ['map', 'compare'] else hide

    if view == 'map':
        return (
            show_map_row, hide_panel, hide_panel, hide_panel, hide_panel,
            geography_style,
            show, show, hide,
            lsoa_filter, lad_filter
        )

    if view == 'compare':
        return (
            hide_map_row, show_panel, hide_panel, hide_panel, hide_panel,
            geography_style,
            hide, hide, show,
            lsoa_filter, lad_filter
        )

    if view == 'stats':
        return (
            hide_map_row, hide_panel, show_panel, hide_panel, hide_panel,
            geography_style,
            hide, hide, hide,
            hide, hide
        )

    if view == 'mismatch':
        return (
            hide_map_row, hide_panel, hide_panel, show_panel, hide_panel,
            geography_style,
            hide, hide, hide,
            hide, hide
        )

    # about
    return (
        hide_map_row, hide_panel, hide_panel, hide_panel, show_panel,
        geography_style,
        hide, hide, hide,
        hide, hide
    )
