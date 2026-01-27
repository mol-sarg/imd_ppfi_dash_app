# callbacks/stats_callbacks.py

from dash import html
from dash.dependencies import Input, Output
from app import app

from utils.data import df_mismatch


@app.callback(
    Output('stats_content', 'children'),
    Input('view_selector', 'value'),
)
def render_stats(view):
    if view != 'stats':
        return []

    mask_valid = df_mismatch['pp_dec_combined'].notna() & df_mismatch['imd_decile'].notna()
    corr = df_mismatch.loc[mask_valid, 'pp_dec_combined'].corr(df_mismatch.loc[mask_valid, 'imd_decile'])

    agreement_within1 = (df_mismatch['abs_diff'] <= 1).mean()
    pct_ppfi_more_vuln = (df_mismatch['ppfi_imd_diff'] < 0).mean()
    pct_ppfi_less_vuln = (df_mismatch['ppfi_imd_diff'] > 0).mean()
    n_total = len(df_mismatch)

    return [
        html.Ul([
            html.Li(f'Number of LSOAs: {n_total:,}'),
            html.Li(f'Correlation (PPFI combined decile vs IMD decile): {corr:.2f}'),
            html.Li(f'Agreement within ±1 decile: {agreement_within1*100:.1f}%'),
            html.Li(f'PPFI shows higher vulnerability than IMD (negative diff): {pct_ppfi_more_vuln*100:.1f}%'),
            html.Li(f'PPFI shows lower vulnerability than IMD (positive diff): {pct_ppfi_less_vuln*100:.1f}%'),
        ]),
        html.H4('Interpretation'),
        html.P(
            'PPFI and IMD are related but not identical. Correlation summarises the overall relationship, '
            'while the differences highlight where PPFI indicates more/less vulnerability than IMD.'
        ),
    ]
