
import plotly.express as px

from utils.constants import (
    PPFI_DOMAINS_LSOA, IMD_DOMAINS_LSOA,
    PPFI_DOMAINS_LAD,  IMD_DOMAINS_LAD,
    PPFI_LSOA_PALETTE, IMD_LSOA_PALETTE,
    PPFI_LAD_PALETTE,  IMD_LAD_PALETTE,
    LSOA_NAME, LAD_NAME,
)

# Full datasets for global colour scaling
from utils.data import gdf_lsoa_full, gdf_lad_full


# domain helpers

def get_domains_for_single(geo: str, dataset: str):
    if geo == 'lsoa' and dataset == 'ppfi':
        return PPFI_DOMAINS_LSOA
    if geo == 'lsoa' and dataset == 'imd':
        return IMD_DOMAINS_LSOA
    if geo == 'lad' and dataset == 'ppfi':
        return PPFI_DOMAINS_LAD
    return IMD_DOMAINS_LAD


def get_domains_for_compare(geo: str):
    if geo == 'lsoa':
        left = PPFI_DOMAINS_LSOA
        right = IMD_DOMAINS_LSOA
    else:
        left = PPFI_DOMAINS_LAD
        right = IMD_DOMAINS_LAD

    return {k: k for k in left.keys() if k in right.keys()}


def _pick_palette(geo: str, dataset: str):
    if geo == 'lsoa':
        return PPFI_LSOA_PALETTE if dataset == 'ppfi' else IMD_LSOA_PALETTE
    return PPFI_LAD_PALETTE if dataset == 'ppfi' else IMD_LAD_PALETTE


def _pretty_domain(domain_key: str) -> str:
    return domain_key.replace('_', ' ').strip().title()


def _first_existing_col(gdf, candidates):
    for c in candidates:
        if c in getattr(gdf, 'columns', []):
            return c
    return None


def _safe_series(gdf, col_name, default=''):
    if col_name and col_name in gdf.columns:
        return gdf[col_name]
    return default


# alignment bands
def _alignment_band(mismatch_value, geography: str, n_lad: int) -> str:
    if mismatch_value is None:
        return ''

    try:
        m = int(mismatch_value)
    except Exception:
        return ''

    # direction phrasing
    if m > 0:
        direction = 'Food-related vulnerability is higher than general deprivation in this area.'
    elif m < 0:
        direction = 'General deprivation is higher than food-related vulnerability in this area.'
    else:
        return 'Alignment: Closely aligned'

    a = abs(m)

    # LSOA uses fixed decile-scale thresholds
    if geography == 'lsoa':
        if a == 1:
            return f'Slightly misaligned: {direction}'
        elif a in (2, 3):
            return f'Moderately misaligned: {direction}'
        else:
            return f'Strongly misaligned: {direction}'

    # LAD thresholds scale by LAD count
    slight_thr = max(1, int(round(0.10 * n_lad)))
    moderate_thr = max(slight_thr + 1, int(round(0.25 * n_lad)))

    if a <= slight_thr:
        return f'Slightly misaligned: {direction}'
    elif a <= moderate_thr:
        return f'Moderately misaligned: {direction}'
    else:
        return f'Strongly misaligned: {direction}'


# map maker

def make_map(
    geography: str,
    dataset: str,
    domain: str,
    gdf_lsoa, geojson_lsoa,
    gdf_lad, geojson_lad
):

    colorscale = _pick_palette(geography, dataset)
    n_lad = int(getattr(gdf_lad_full, 'shape', [0])[0] or 0)

    # LSOA
    if geography == 'lsoa':
        gdf = gdf_lsoa.copy()
        geojson = geojson_lsoa

        color_col = (
            PPFI_DOMAINS_LSOA[domain]
            if dataset == 'ppfi' else
            IMD_DOMAINS_LSOA[domain]
        )

        range_color = (1, 10)
        colorbar_title = 'Decile'

        # LSOA NAME
        lsoa_name_col = _first_existing_col(
            gdf,
            [LSOA_NAME, 'LSOA21NM', 'LSOA11NM', 'lsoa_name', 'name']
        )
        gdf['hover_lsoa_name'] = _safe_series(gdf, lsoa_name_col, default='')

        # combined columns 
        gdf['hover_ppfi_combined'] = gdf['pp_dec_combined'] if 'pp_dec_combined' in gdf.columns else None
        gdf['hover_imd_combined'] = gdf['imd_decile'] if 'imd_decile' in gdf.columns else None

        if 'pp_dec_combined' in gdf.columns and 'imd_decile' in gdf.columns:
            gdf['hover_mismatch'] = gdf['pp_dec_combined'] - gdf['imd_decile']
        else:
            gdf['hover_mismatch'] = None

        gdf['hover_alignment'] = gdf['hover_mismatch'].apply(
            lambda v: _alignment_band(v, 'lsoa', n_lad)
        )

        pretty = _pretty_domain(domain)
        if domain != 'combined':
            dom_col = (
                PPFI_DOMAINS_LSOA[domain] if dataset == 'ppfi'
                else IMD_DOMAINS_LSOA[domain]
            )
            if dom_col in gdf.columns:
                gdf['hover_domain_line'] = (
                    f'{pretty} decile ({dataset.upper()}): ' +
                    gdf[dom_col].astype(str)
                )
            else:
                gdf['hover_domain_line'] = ''
        else:
            gdf['hover_domain_line'] = ''

        # LSOA layout
        customdata = gdf[[
            'hover_lsoa_name',        # 0
            'hover_ppfi_combined',    # 1
            'hover_imd_combined',     # 2
            'hover_mismatch',         # 3
            'hover_alignment',        # 4
            'hover_domain_line',      # 5
        ]].values

        hovertemplate = (
            '<b>%{customdata[0]}</b><br>'
            'PPFI combined (decile): %{customdata[1]}<br>'
            'IMD combined (decile): %{customdata[2]}<br>'
            'Difference (PPFI − IMD): %{customdata[3]}<br>'
            '%{customdata[4]}<br>'
            '%{customdata[5]}<br><br>'
            '<extra></extra>'
        )

    # local authority
    else:
        gdf = gdf_lad.copy()
        geojson = geojson_lad

        color_col = (
            PPFI_DOMAINS_LAD[domain]
            if dataset == 'ppfi' else
            IMD_DOMAINS_LAD[domain]
        )

        full_max = gdf_lad_full[color_col].max() if color_col in gdf_lad_full.columns else None
        range_color = (1, full_max) if full_max is not None else None
        colorbar_title = 'Rank'

        # LAD NAME 
        lad_name_col = _first_existing_col(
            gdf,
            [
                LAD_NAME,
                'LAD24NM', 'LAD24NM_x', 'LAD24NM_y',
                'LAD23NM', 'LAD22NM', 'LAD21NM',
                'lad_name', 'NAME', 'name'
            ]
        )
        gdf['hover_lad_name'] = _safe_series(gdf, lad_name_col, default='')

        # combined columns
        gdf['hover_ppfi_combined'] = gdf['combined'] if 'combined' in gdf.columns else None
        gdf['hover_imd_combined'] = gdf['imd_rank'] if 'imd_rank' in gdf.columns else None

        if 'combined' in gdf.columns and 'imd_rank' in gdf.columns:
            gdf['hover_mismatch'] = gdf['combined'] - gdf['imd_rank']
        else:
            gdf['hover_mismatch'] = None

        gdf['hover_alignment'] = gdf['hover_mismatch'].apply(
            lambda v: _alignment_band(v, 'lad', n_lad)
        )

        pretty = _pretty_domain(domain)
        if domain != 'combined':
            dom_col = (
                PPFI_DOMAINS_LAD[domain] if dataset == 'ppfi'
                else IMD_DOMAINS_LAD[domain]
            )
            if dom_col in gdf.columns:
                gdf['hover_domain_line'] = (
                    f'{pretty} rank ({dataset.upper()}): ' +
                    gdf[dom_col].astype(str)
                )
            else:
                gdf['hover_domain_line'] = ''
        else:
            gdf['hover_domain_line'] = ''

        # LAD layout
        customdata = gdf[[
            'hover_lad_name',         # 0
            'hover_ppfi_combined',    # 1
            'hover_imd_combined',     # 2
            'hover_mismatch',         # 3
            'hover_alignment',        # 4
            'hover_domain_line',      # 5
        ]].values

        hovertemplate = (
            '<b>%{customdata[0]}</b><br><br>'
            'PPFI combined (rank): %{customdata[1]}<br>'
            'IMD combined (rank): %{customdata[2]}<br>'
            'Difference (PPFI − IMD): %{customdata[3]}<br>'
            '%{customdata[4]}<br>'
            '%{customdata[5]}<br><br>'
            '<extra></extra>'
        )

    # build figure
    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson,
        locations='id',
        featureidkey='properties.id',
        color=color_col,
        range_color=range_color,
        color_continuous_scale=colorscale,
        opacity=0.85,
    )

    fig.update_traces(
        customdata=customdata,
        hovertemplate=hovertemplate,
        marker_line_width=0.3,
    )

    fig.update_layout(
        mapbox=dict(
            style='carto-positron',
            zoom=5.3,
            center={'lat': 53.7, 'lon': -1.5},
        ),
        dragmode='zoom',
        clickmode='event+select',
        uirevision='keep',
        title={
            'text': f'{dataset.upper()} – {_pretty_domain(domain)} ({geography.upper()})',
            'x': 0.5,
        },
        margin={'l': 0, 'r': 0, 't': 40, 'b': 0},
        coloraxis_colorbar={
            'title': colorbar_title,
            'thickness': 12,
            'len': 0.5,
            'y': 0.5,
        },
    )

    return fig


# highlight outline

def add_highlight_outline(fig, gdf, geojson, feature_id: str):
    return fig
