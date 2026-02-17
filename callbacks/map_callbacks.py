# callbacks/map_callbacks.py
import math
import dash
from dash import no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output

from app import app

from utils.data import gdf_lsoa, geojson_lsoa, gdf_lad, geojson_lad
from utils.figures import make_map, get_domains_for_single, get_domains_for_compare
from utils.constants import (
    PPFI_DOMAINS_LAD, IMD_DOMAINS_LAD,
    PPFI_DOMAINS_LSOA, IMD_DOMAINS_LSOA,
)

# helpers

def _to_int_list(v):
    if not v: return []
    if isinstance(v, (list, tuple, set)):
        return [int(x) for x in v if str(x).isdigit()]
    return [int(v)] if str(v).isdigit() else []


def _filter_lsoa_by_deciles(gdf, dataset, domain, deciles):
    decs = _to_int_list(deciles)
    if not decs: return gdf
    col = PPFI_DOMAINS_LSOA.get(domain) if dataset=="ppfi" else IMD_DOMAINS_LSOA.get(domain)
    return gdf[gdf[col].isin(decs)] if col in gdf.columns else gdf


def _filter_lad_by_percent(gdf, dataset, domain, pct):
    if pct is None: return gdf
    col = PPFI_DOMAINS_LAD.get(domain) if dataset=="ppfi" else IMD_DOMAINS_LAD.get(domain)
    if col not in gdf.columns: return gdf
    max_rank = gdf[col].max()
    cutoff = int((pct/100)*max_rank)
    return gdf[gdf[col] <= cutoff]


def _filter_lsoa_to_selected_lad(gdf, data):
    if not data or "lad_id" not in data: 
        return gdf
    lad_id = data["lad_id"]
    return gdf[gdf["lad_cd"] == lad_id] if "lad_cd" in gdf.columns else gdf


def _center_zoom(bounds):
    minx, miny, maxx, maxy = bounds
    center = {"lon": (minx+maxx)/2, "lat": (miny+maxy)/2}
    span = max(maxx-minx, maxy-miny)
    zoom = 8.5 - math.log(span+1e-9, 2)
    return center, max(5.3, min(10.5, zoom))


# drilldown

@app.callback(
    Output("selected_lad_store","data"),
    Output("geography_selector","value"),
    Input("map_single","clickData"),
    Input("map_compare_left","clickData"),
    Input("map_compare_right","clickData"),
    Input("geography_selector","value"),
    Input("view_selector","value"),
    prevent_initial_call=True,
)
def drill(click_single, click_left, click_right, geo, view):
    ctx = dash.callback_context
    trig = ctx.triggered[0]["prop_id"].split(".")[0]

    # reset when return to lad
    if trig=="geography_selector" and geo=="lad":
        return None, no_update

    def parse(cd):
        if not cd: return (None,None)
        pt = cd["points"][0]
        return pt.get("location") or pt.get("id"), (pt.get("customdata") or [None])[0]

    # Single map
    if trig=="map_single" and view=="map" and geo=="lad":
        lad_id, lad_name = parse(click_single)
        if lad_id: return {"lad_id":lad_id,"lad_name":lad_name}, "lsoa"

    # Compare maps
    if view=="compare" and geo=="lad":
        for t,d in [("map_compare_left",click_left),("map_compare_right",click_right)]:
            if trig==t:
                lad_id, lad_name = parse(d)
                if lad_id: return {"lad_id":lad_id,"lad_name":lad_name}, "lsoa"

    raise PreventUpdate


# domain dropdown

@app.callback(
    Output("domain_selector","options"),
    Output("domain_selector","value"),
    Input("view_selector","value"),
    Input("geography_selector","value"),
    Input("dataset_selector","value"),
    Input("domain_selector","value"),
)
def update_domain_opts(view, geo, dataset, cur):
    domains = get_domains_for_compare(geo) if view=="compare" else get_domains_for_single(geo,dataset)
    opts = [{"label": k.replace("_"," ").title(), "value": k} for k in domains]
    if cur not in domains: cur="combined"
    return opts, cur


# single map

@app.callback(
    Output("map_single","figure"),
    Input("geography_selector","value"),
    Input("dataset_selector","value"),
    Input("domain_selector","value"),
    Input("view_selector","value"),
    Input("lsoa_decile_filter","value"),
    Input("lad_rank_filter","value"),
    Input("selected_lad_store","data"),
)
def update_single(geo, dataset, domain, view, deciles, pct, sel):
    fl = gdf_lsoa.copy()
    fa = gdf_lad.copy()

    if geo=="lsoa":
        fl = _filter_lsoa_by_deciles(fl, dataset, domain, deciles)
        fl = _filter_lsoa_to_selected_lad(fl, sel)

    else:
        fa = _filter_lad_by_percent(fa, dataset, domain, pct)

    fig = make_map(geo, dataset, domain, fl, geojson_lsoa, fa, geojson_lad)

    if geo=="lsoa" and sel and not fl.empty:
        center, zoom = _center_zoom(fl.total_bounds)
        fig.update_layout(mapbox_center=center, mapbox_zoom=zoom)

    return fig


# compare maps

@app.callback(
    Output("map_compare_left","figure"),
    Output("map_compare_right","figure"),
    Input("geography_selector","value"),
    Input("domain_selector_ppfi","value"),
    Input("domain_selector_imd","value"),
    Input("lsoa_decile_filter","value"),
    Input("lad_rank_filter","value"),
    Input("view_selector","value"),
    Input("selected_lad_store","data"),
)
def do_compare(geo, dom_ppfi, dom_imd, deciles, pct, view, sel):

    lsoa = gdf_lsoa.copy()
    lad  = gdf_lad.copy()

    lsoa["compare_view"] = True
    lad["compare_view"] = True

    if geo=="lsoa":
        left_lsoa  = _filter_lsoa_by_deciles(lsoa,"ppfi",dom_ppfi,deciles)
        right_lsoa = _filter_lsoa_by_deciles(lsoa,"imd", dom_imd, deciles)
        left_lsoa  = _filter_lsoa_to_selected_lad(left_lsoa, sel)
        right_lsoa = _filter_lsoa_to_selected_lad(right_lsoa, sel)

        left_lad = lad
        right_lad = lad

    else:
        left_lsoa = right_lsoa = lsoa
        left_lad  = _filter_lad_by_percent(lad,"ppfi",dom_ppfi,pct)
        right_lad = _filter_lad_by_percent(lad,"imd", dom_imd,pct)

    left_fig = make_map(
        geo, "ppfi", dom_ppfi,
        left_lsoa, geojson_lsoa,
        left_lad,  geojson_lad,
        compact_hover=True,
    )

    right_fig = make_map(
        geo, "imd", dom_imd,
        right_lsoa, geojson_lsoa,
        right_lad,  geojson_lad,
        compact_hover=True,
    )

    # drilldown zoom
    if geo=="lsoa" and sel:
        target = left_lsoa if not left_lsoa.empty else right_lsoa
        if not target.empty:
            center, zoom = _center_zoom(target.total_bounds)
            left_fig.update_layout(mapbox_center=center, mapbox_zoom=zoom)
            right_fig.update_layout(mapbox_center=center, mapbox_zoom=zoom)

    return left_fig, right_fig