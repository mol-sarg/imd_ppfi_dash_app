
# callbacks/map_callbacks.py
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

# filter lsoa gdf by one or more deciles for chosen data/domain
def _filter_lsoa_by_deciles(gdf, dataset: str, domain: str, deciles_value):
    deciles = _to_int_list(deciles_value)
    if not deciles:
        return gdf

    col = (PPFI_DOMAINS_LSOA[domain] if dataset == 'ppfi' else IMD_DOMAINS_LSOA[domain])
    if col not in gdf.columns:
        return gdf

    return gdf[gdf[col].isin(deciles)]


# filter LAD gdf by lowest rank % for chosen data/domain
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


# domain options
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
)
def update_map(
    geography,
    dataset,
    domain,
    view,
    lsoa_decile,
    lad_percent,
):
    filtered_lsoa = gdf_lsoa.copy()
    filtered_lad = gdf_lad.copy()

    if geography == 'lsoa':
        # multi-decile filter
        filtered_lsoa = _filter_lsoa_by_deciles(filtered_lsoa, dataset, domain, lsoa_decile)

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
    )

    return fig


# compare maps, independent filtering per panel
@app.callback(
    Output('map_compare_left', 'figure'),
    Output('map_compare_right', 'figure'),
    Input('geography_selector', 'value'),
    Input('domain_selector_ppfi', 'value'),
    Input('domain_selector_imd', 'value'),
    Input('lsoa_decile_filter', 'value'),
    Input('lad_rank_filter', 'value'),
    Input('view_selector', 'value'),
)
def update_compare_maps(
    geography,
    domain_ppfi,
    domain_imd,
    lsoa_decile,
    lad_percent,
    view,
):
    lsoa_base = gdf_lsoa.copy()
    lad_base = gdf_lad.copy()

    if geography == 'lsoa':
        # multi-decile, independent by dataset
        filtered_lsoa_left = _filter_lsoa_by_deciles(lsoa_base, 'ppfi', domain_ppfi, lsoa_decile)
        filtered_lsoa_right = _filter_lsoa_by_deciles(lsoa_base, 'imd', domain_imd, lsoa_decile)

        filtered_lad_left = lad_base
        filtered_lad_right = lad_base

    else:
        filtered_lsoa_left = lsoa_base
        filtered_lsoa_right = lsoa_base

        # independent LAD filtering per dataset
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
    )

    right_fig = make_map(
        geography,
        'imd',
        domain_imd,
        filtered_lsoa_right,
        geojson_lsoa,
        filtered_lad_right,
        geojson_lad,
    )

    return left_fig, right_fig
