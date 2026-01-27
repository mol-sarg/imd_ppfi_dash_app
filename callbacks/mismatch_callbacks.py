# callbacks/mismatch_callbacks.py

from dash.dependencies import Input, Output
from app import app

from utils.data import df_mismatch 


LSOA_CODE_COL = 'lsoa21cd'
LSOA_NAME_COL = 'lsoa21nm'
LAD_NAME_COL = 'lad24nm'


@app.callback(
    Output('mismatch_lad_filter', 'options'),
    Input('view_selector', 'value'),
)
def populate_lad_dropdown(view):
    if view != 'mismatch':
        return []
    if LAD_NAME_COL not in df_mismatch.columns:
        return []
    return [{'label': lad, 'value': lad} for lad in sorted(df_mismatch[LAD_NAME_COL].dropna().unique())]


@app.callback(
    Output('mismatch_table', 'columns'),
    Output('mismatch_table', 'data'),
    Input('view_selector', 'value'),
    Input('mismatch_lad_filter', 'value'),
)
def mismatch_table(view, lad):
    if view != 'mismatch':
        return [], []

    dff = df_mismatch
    if lad and LAD_NAME_COL in dff.columns:
        dff = dff[dff[LAD_NAME_COL] == lad]

    cols = [
        {'name': 'LSOA code', 'id': LSOA_CODE_COL},
        {'name': 'LSOA name', 'id': LSOA_NAME_COL},
        {'name': 'Local authority', 'id': LAD_NAME_COL},
        {'name': 'PPFI decile', 'id': 'pp_dec_combined', 'type': 'numeric'},
        {'name': 'IMD decile', 'id': 'imd_decile', 'type': 'numeric'},
        {'name': 'PPFI – IMD', 'id': 'ppfi_imd_diff', 'type': 'numeric'},
        {'name': '|difference|', 'id': 'abs_diff', 'type': 'numeric'},
    ]

    return cols, dff.to_dict('records')
