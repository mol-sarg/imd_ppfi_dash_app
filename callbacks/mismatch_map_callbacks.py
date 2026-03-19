# callbacks/mismatch_map_callbacks.py
import plotly.express as px
from dash.dependencies import Input, Output

from app import app
from utils.data import gdf_lsoa, geojson_lsoa
from utils.constants import PPFI_LSOA_PALETTE

# Pre-compute abs_diff once
_gdf = gdf_lsoa.copy()
_gdf['abs_diff'] = (_gdf['pp_dec_combined'] - _gdf['imd_decile']).abs()


@app.callback(
    Output('mismatch_map', 'figure'),
    Input('mismatch_threshold_slider', 'value'),
)
def update_mismatch_map(threshold):
    filtered = _gdf[_gdf['abs_diff'] >= threshold]

    fig = px.choropleth_mapbox(
        filtered,
        geojson=geojson_lsoa,
        locations='id',
        featureidkey='properties.id',
        color='abs_diff',
        color_continuous_scale=PPFI_LSOA_PALETTE[::-1],
        range_color=(0, 9),
        opacity=0.85,
    )

    fig.update_layout(
        mapbox=dict(
            style='carto-positron',
            zoom=5.3,
            center={'lat': 53.7, 'lon': -1.5},
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        uirevision='mismatch_map',
        coloraxis_colorbar=dict(title='Abs diff', thickness=12, len=0.5),
        title={
            'text': f'PPFI vs IMD — absolute decile difference (threshold ≥ {threshold})',
            'x': 0.5,
        },
    )

    fig.update_traces(marker_line_width=0.0)

    return fig