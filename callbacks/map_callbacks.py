# callbacks/map_callbacks.py
import math
import dash
from dash import no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output

from app import app

from utils.data import gdf_lsoa, geojson_lsoa, gdf_lad, geojson_lad
from utils.figures import (
    make_map,
    get_domains_for_single,
    get_domains_for_compare,
)
from utils.constants import (
    PPFI_DOMAINS_LAD,
    IMD_DOMAINS_LAD,
    PPFI_DOMAINS_LSOA,
    IMD_DOMAINS_LSOA,
)

# helpers
def _to_int_list(v):
    if v is None or v == '' or v == 'All':
        return []
    if isinstance(v, (list, tuple, set)):
        out = []
        for item in v:
            try:
                out.append(int(item))
            except Exception:
                pass
        return out
    try:
        return [int(v)]
    except Exception:
        return []


def _filter_lsoa_by_deciles(gdf, dataset: str, domain: str, deciles_value):
    deciles = _to_int_list(deciles_value)
    if not deciles:
        return gdf
    col = (PPFI_DOMAINS_LSOA[domain] if dataset == 'ppfi' else IMD_DOMAINS_LSOA[domain])
    if col not in gdf.columns:
        return gdf
    return gdf[gdf[col].isin(deciles)]


def _filter_lad_by_percent(gdf, dataset: str, domain: str, lad_percent):
    if lad_percent is None:
        return gdf
    rank_col = (PPFI_DOMAINS_LAD[domain] if dataset == 'ppfi' else IMD_DOMAINS_LAD[domain])
    if rank_col not in gdf.columns:
        return gdf
    max_rank_val = gdf[rank_col].max()
    if max_rank_val is None:
        return gdf
    max_rank = int((lad_percent / 100) * max_rank_val)
    return gdf[gdf[rank_col] <= max_rank]


def _filter_lsoa_to_selected_lad(gdf, selected_lad):
    if not selected_lad or not isinstance(selected_lad, dict):
        return gdf
    lad_id = selected_lad.get('lad_id')
    if not lad_id:
        return gdf
    if 'lad_cd' not in gdf.columns:
        return gdf
    return gdf[gdf['lad_cd'] == lad_id]


def _center_zoom_from_bounds(bounds):
    minx, miny, maxx, maxy = bounds
    center = {'lon': (minx + maxx) / 2, 'lat': (miny + maxy) / 2}
    span = max(maxx - minx, maxy - miny)
    if span <= 0:
        zoom = 9.5
    else:
        zoom = 8.5 - math.log(span + 1e-9, 2)
    zoom = max(5.3, min(10.5, zoom))
    return center, zoom


def _extract_lad_from_click(clickData):
    if not clickData or not clickData.get('points'):
        return None, None
    pt = clickData['points'][0]
    lad_id = pt.get('location') or pt.get('id')
    lad_name = None
    cd = pt.get('customdata')
    if isinstance(cd, (list, tuple)) and len(cd) > 0:
        lad_name = cd[0]
    return lad_id, lad_name


# drilldown
@app.callback(
    Output('selected_lad_store', 'data'),
    Output('geography_selector', 'value'),
    Input('map_single', 'clickData'),
    Input('map_compare_left', 'clickData'),
    Input('map_compare_right', 'clickData'),
    Input('geography_selector', 'value'),
    Input('view_selector', 'value'),
    prevent_initial_call=True,
)
def drilldown_lad_to_lsoa(click_single, click_left, click_right, geography, view):
    triggered = (
        dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        if dash.callback_context.triggered
        else None
    )

    if triggered == 'geography_selector' and geography == 'lad':
        return None, no_update

    if geography != 'lad':
        raise PreventUpdate

    if view == 'map' and triggered == 'map_single':
        lad_id, lad_name = _extract_lad_from_click(click_single)
        if lad_id:
            return {'lad_id': lad_id, 'lad_name': lad_name}, 'lsoa'
        raise PreventUpdate

    if view == 'compare' and triggered in ('map_compare_left', 'map_compare_right'):
        clickData = click_left if triggered == 'map_compare_left' else click_right
        lad_id, lad_name = _extract_lad_from_click(clickData)
        if lad_id:
            return {'lad_id': lad_id, 'lad_name': lad_name}, 'lsoa'
        raise PreventUpdate

    raise PreventUpdate


# domain opts
@app.callback(
    Output('domain_selector', 'options'),
    Output('domain_selector', 'value'),
    Input('view_selector', 'value'),
    Input('geography_selector', 'value'),
    Input('dataset_selector', 'value'),
    Input('domain_selector', 'value'),
)
def update_domain_options(view, geo, dataset, current_domain):
    domains = get_domains_for_compare(geo) if view == 'compare' else get_domains_for_single(geo, dataset)
    opts = [{'label': k.replace('_', ' ').title(), 'value': k} for k in domains.keys()]
    if current_domain not in domains:
        current_domain = 'combined'
    return opts, current_domain


# single map
@app.callback(
    Output('map_single', 'figure'),
    Input('geography_selector', 'value'),
    Input('dataset_selector', 'value'),
    Input('domain_selector', 'value'),
    Input('view_selector', 'value'),
    Input('lsoa_decile_filter', 'value'),
    Input('lad_rank_filter', 'value'),
    Input('selected_lad_store', 'data'),
)
def update_map(geography, dataset, domain, view, lsoa_decile, lad_percent, selected_lad):
    filtered_lsoa = gdf_lsoa.copy()
    filtered_lad = gdf_lad.copy()

    if geography == 'lsoa':
        filtered_lsoa = _filter_lsoa_by_deciles(filtered_lsoa, dataset, domain, lsoa_decile)
        filtered_lsoa = _filter_lsoa_to_selected_lad(filtered_lsoa, selected_lad)

    if geography == 'lad':
        filtered_lad = _filter_lad_by_percent(filtered_lad, dataset, domain, lad_percent)

    fig = make_map(
        geography,
        dataset,
        domain,
        filtered_lsoa,
        geojson_lsoa,
        filtered_lad,
        geojson_lad,
        selected_lad=selected_lad,  
    )

    if geography == 'lsoa' and selected_lad and hasattr(filtered_lsoa, 'empty') and not filtered_lsoa.empty:
        try:
            minx, miny, maxx, maxy = filtered_lsoa.total_bounds
            center, zoom = _center_zoom_from_bounds((minx, miny, maxx, maxy))
            fig.update_layout(mapbox_center=center, mapbox_zoom=zoom)

            lad_label = selected_lad.get('lad_name') or selected_lad.get('lad_id')
            if lad_label:
                fig.update_layout(
                    title={'text': f'{dataset.upper()} – {domain.replace("_"," ").title()} (LSOA) within {lad_label}', 'x': 0.5}
                )
        except Exception:
            pass

    return fig


# compare maps
@app.callback(
    Output('map_compare_left', 'figure'),
    Output('map_compare_right', 'figure'),
    Input('geography_selector', 'value'),
    Input('domain_selector_ppfi', 'value'),
    Input('domain_selector_imd', 'value'),
    Input('lsoa_decile_filter', 'value'),
    Input('lad_rank_filter', 'value'),
    Input('view_selector', 'value'),
    Input('selected_lad_store', 'data'),
)
def update_compare_maps(geography, domain_ppfi, domain_imd, lsoa_decile, lad_percent, view, selected_lad):
    lsoa_base = gdf_lsoa.copy()
    lad_base = gdf_lad.copy()

    if geography == 'lsoa':
        filtered_lsoa_left = _filter_lsoa_by_deciles(lsoa_base, 'ppfi', domain_ppfi, lsoa_decile)
        filtered_lsoa_right = _filter_lsoa_by_deciles(lsoa_base, 'imd', domain_imd, lsoa_decile)

        filtered_lsoa_left = _filter_lsoa_to_selected_lad(filtered_lsoa_left, selected_lad)
        filtered_lsoa_right = _filter_lsoa_to_selected_lad(filtered_lsoa_right, selected_lad)

        filtered_lad_left = lad_base
        filtered_lad_right = lad_base
    else:
        filtered_lsoa_left = lsoa_base
        filtered_lsoa_right = lsoa_base

        filtered_lad_left = _filter_lad_by_percent(lad_base, 'ppfi', domain_ppfi, lad_percent)
        filtered_lad_right = _filter_lad_by_percent(lad_base, 'imd', domain_imd, lad_percent)

    left_fig = make_map(
        geography,
        'ppfi',
        domain_ppfi,
        filtered_lsoa_left,
        geojson_lsoa,
        filtered_lad_left,
        geojson_lad,
        compact_hover=True,
        selected_lad=selected_lad,  
    )

    right_fig = make_map(
        geography,
        'imd',
        domain_imd,
        filtered_lsoa_right,
        geojson_lsoa,
        filtered_lad_right,
        geojson_lad,
        compact_hover=True,
        selected_lad=selected_lad, 
    )

    if geography == 'lsoa' and selected_lad:
        bounds_gdf = filtered_lsoa_left if hasattr(filtered_lsoa_left, 'empty') and not filtered_lsoa_left.empty else filtered_lsoa_right
        if bounds_gdf is not None and hasattr(bounds_gdf, 'empty') and not bounds_gdf.empty:
            try:
                minx, miny, maxx, maxy = bounds_gdf.total_bounds
                center, zoom = _center_zoom_from_bounds((minx, miny, maxx, maxy))
                left_fig.update_layout(mapbox_center=center, mapbox_zoom=zoom)
                right_fig.update_layout(mapbox_center=center, mapbox_zoom=zoom)
            except Exception:
                pass

    pretty_ppfi = domain_ppfi.replace("_"," ").title()
    pretty_imd  = domain_imd.replace("_"," ").title()
    geo_label   = geography.upper()

    if not selected_lad:
        left_fig.update_layout(title={"text": f"PPFI – {pretty_ppfi} ({geo_label})", "x": 0.5})
        right_fig.update_layout(title={"text": f"IMD – {pretty_imd} ({geo_label})", "x": 0.5})
        return left_fig, right_fig

    lad_label = selected_lad.get("lad_name") or selected_lad.get("lad_id")
    left_fig.update_layout(title={"text": f"PPFI – {pretty_ppfi} ({geo_label}) within {lad_label}", "x": 0.5})
    right_fig.update_layout(title={"text": f"IMD – {pretty_imd} ({geo_label}) within {lad_label}", "x": 0.5})
    return left_fig, right_fig
