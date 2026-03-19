# callbacks/navigation_callbacks.py
from dash.dependencies import Input, Output
from app import app


@app.callback(
    Output("map_row", "style"),
    Output("compare_panel", "style"),
    Output("mismatch_panel", "style"),
    Output("about_panel", "style"),
    Output("mismatch_map_panel", "style"),


    Output("geography_block", "style"),
    Output("dataset_block", "style"),
    Output("domain_block", "style"),
    Output("compare_domains_block", "style"),
    Output("lsoa_decile_filter_block", "style"),
    Output("lad_rank_filter_block", "style"),
    Output("mismatch_threshold_block", "style"),


    Input("view_selector", "value"),
    Input("geography_selector", "value"),
)
def switch_view(view, geo):

    show = {"display": "block"}
    hide = {"display": "none"}

    # full-height views
    show_map = {
        "display": "flex",
        "flexDirection": "column",
        "height": "100%",
        "minHeight": 0,
        "minWidth": 0,
    }

    show_compare = {
        "display": "flex",
        "flexDirection": "column",
        "height": "100%",
        "minHeight": 0,
        "minWidth": 0,
        "gap": "10px",
    }
    show_mismatch_map = {
        "display": "flex",
        "flexDirection": "column",
        "flex": 1,
        "minHeight": 0,
        "boxSizing": "border-box",
        "padding": "16px",
    }

    # normal page views (About + Mismatch)
    show_page = {
        "display": "block",
        "marginTop": "10px",
        "padding": "16px",
        "boxSizing": "border-box",
        "overflowY": "auto",
    }

    # geography controls visible for map + compare only
    geography_style = show if view in ["map", "compare"] else hide

    lsoa_filter = show if geo == "lsoa" and view in ["map", "compare"] else hide
    lad_filter = show if geo == "lad" and view in ["map", "compare"] else hide


    if view == "map":
        return (
            show_map, hide, hide, hide, hide,
            geography_style,
            show, show, hide,
            lsoa_filter, lad_filter, hide
        )


    if view == "compare":
        return (
            hide, show_compare, hide, hide, hide,
            geography_style,
            hide, hide, show,
            lsoa_filter, lad_filter, hide
        )


    if view == "mismatch":
        return (
            hide, hide, show_page, hide, hide,
            hide,
            hide, hide, hide,
            hide, hide, hide
        )
    
    if view == "mismatch_map":
        return (
            hide, hide, hide, hide, show_mismatch_map,
            hide,
            hide, hide, hide,
            hide, hide, show
        )


    # about
    return (
        hide, hide, hide, show_page, hide,
        hide,
        hide, hide, hide,
        hide, hide, hide
    )
