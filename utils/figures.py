#utils/figures.py
import plotly.express as px

from utils.constants import (
    PPFI_DOMAINS_LSOA, IMD_DOMAINS_LSOA,
    PPFI_DOMAINS_LAD,  IMD_DOMAINS_LAD,
    PPFI_LSOA_PALETTE, IMD_LSOA_PALETTE,
    PPFI_LAD_PALETTE,  IMD_LAD_PALETTE,
    LSOA_NAME, LAD_NAME,
)

from utils.data import gdf_lsoa_full, gdf_lad_full


# helpers

def get_domains_for_single(geo: str, dataset: str):
    if geo == "lsoa" and dataset == "ppfi":
        return PPFI_DOMAINS_LSOA
    if geo == "lsoa" and dataset == "imd":
        return IMD_DOMAINS_LSOA
    if geo == "lad" and dataset == "ppfi":
        return PPFI_DOMAINS_LAD
    return IMD_DOMAINS_LAD


def get_domains_for_compare(geo: str):
    if geo == "lsoa":
        keys = set(PPFI_DOMAINS_LSOA.keys()) | set(IMD_DOMAINS_LSOA.keys())
    else:
        keys = set(PPFI_DOMAINS_LAD.keys()) | set(IMD_DOMAINS_LAD.keys())

    return {k: k for k in sorted(keys)}


def _pick_palette(geo: str, dataset: str):
    if geo == "lsoa":
        return PPFI_LSOA_PALETTE if dataset == "ppfi" else IMD_LSOA_PALETTE
    return PPFI_LAD_PALETTE if dataset == "ppfi" else IMD_LAD_PALETTE


def _pretty_domain(domain_key: str):
    return domain_key.replace("_", " ").strip().title()


def _first_existing_col(gdf, candidates):
    for c in candidates:
        if c in getattr(gdf, "columns", []):
            return c
    return None


def _safe_series(gdf, col_name, default=""):
    if col_name and col_name in gdf.columns:
        return gdf[col_name]
    return default


def _safe(gdf, col):
    return gdf[col] if col and col in gdf.columns else None

def _alignment_band(mismatch_value, geography: str, n_lad: int):
    if mismatch_value is None:
        return ""

    try:
        m = int(mismatch_value)
    except Exception:
        return ""

    if m > 0:
        direction = "Food-related vulnerability is higher than general deprivation in this area."
    elif m < 0:
        direction = "General deprivation is higher than food-related vulnerability in this area."
    else:
        return "Alignment: Closely aligned"

    a = abs(m)

    if geography == "lsoa":
        if a == 1:
            return f"Slightly misaligned: {direction}"
        elif a in (2, 3):
            return f"Moderately misaligned: {direction}"
        else:
            return f"Strongly misaligned: {direction}"

    slight_thr = max(1, int(round(0.10 * n_lad)))
    moderate_thr = max(slight_thr + 1, int(round(0.25 * n_lad)))

    if a <= slight_thr:
        return f"Slightly misaligned: {direction}"
    elif a <= moderate_thr:
        return f"Moderately misaligned: {direction}"
    else:
        return f"Strongly misaligned: {direction}"

def make_map(
    geography: str,
    dataset: str,
    domain: str,
    gdf_lsoa, geojson_lsoa,
    gdf_lad, geojson_lad,
    *,
    compact_hover: bool = False
):
    pretty = _pretty_domain(domain)
    metric = "Decile" if geography == "lsoa" else "Rank"

    if geography == "lsoa":
        gdf = gdf_lsoa.copy()
        geojson = geojson_lsoa
        dom_ppfi = PPFI_DOMAINS_LSOA.get(domain)
        dom_imd  = IMD_DOMAINS_LSOA.get(domain)
        range_color = (1, 10)
        colorbar_title = "Decile"
        name_col = _first_existing_col(
            gdf, [LSOA_NAME,"LSOA21NM","LSOA11NM","lsoa_name","name"]
        )
    else:
        gdf = gdf_lad.copy()
        geojson = geojson_lad
        dom_ppfi = PPFI_DOMAINS_LAD.get(domain)
        dom_imd  = IMD_DOMAINS_LAD.get(domain)
        full_max = gdf_lad_full[dom_ppfi].max() if dom_ppfi in gdf_lad_full else None
        range_color = (1, full_max) if full_max else None
        colorbar_title = "Rank"
        name_col = _first_existing_col(
            gdf, [LAD_NAME,"LAD24NM","LAD23NM","lad_name","NAME","name"]
        )

    color_col = dom_ppfi if dataset == "ppfi" else dom_imd
    colorscale = _pick_palette(geography, dataset)

    gdf["name"] = _safe_series(gdf, name_col, "")

    if compact_hover:
        gdf["ppfi_val"] = _safe(gdf, dom_ppfi)
        gdf["imd_val"]  = _safe(gdf, dom_imd)

        customdata = gdf[["name","ppfi_val","imd_val"]].values

        if domain == "combined":
            hovertemplate = (
                "<b>%{customdata[0]}</b><br>"
                f"Combined {metric}<br>"
                "PPFI: %{customdata[1]}<br>"
                "IMD: %{customdata[2]}<br>"
                "<extra></extra>"
            )
        else:
            if dataset == "ppfi":
                hovertemplate = (
                    "<b>%{customdata[0]}</b><br>"
                    f"{pretty} {metric}<br>"
                    "PPFI: %{customdata[1]}<br>"
                    "<extra></extra>"
                )
            else:
                hovertemplate = (
                    "<b>%{customdata[0]}</b><br>"
                    f"{pretty} {metric}<br>"
                    "IMD: %{customdata[2]}<br>"
                    "<extra></extra>"
                )

    else:

        if geography == "lsoa":
            ppfi_comb = _safe(gdf,"pp_dec_combined")
            imd_comb  = _safe(gdf,"imd_decile")
        else:
            ppfi_comb = _safe(gdf,"combined")
            imd_comb  = _safe(gdf,"imd_rank")

        gdf["ppfi_combined"] = ppfi_comb
        gdf["imd_combined"]  = imd_comb

        if ppfi_comb is not None and imd_comb is not None:
            gdf["diff"] = gdf["ppfi_combined"] - gdf["imd_combined"]
        else:
            gdf["diff"] = None

        gdf["align"] = gdf["diff"].apply(
            lambda v: _alignment_band(v, geography, len(gdf_lad_full))
        )

        if domain != "combined" and color_col in gdf.columns:
            gdf["domain_line"] = f"{pretty} {metric} ({dataset.upper()}): " + gdf[color_col].astype(str)
        else:
            gdf["domain_line"] = ""

        customdata = gdf[[
            "name",             # 0
            "ppfi_combined",    # 1
            "imd_combined",     # 2
            "diff",             # 3
            "align",            # 4
            "domain_line",      # 5
        ]].values

        hovertemplate = (
            "<b>%{customdata[0]}</b><br>"
            "PPFI combined: %{customdata[1]}<br>"
            "IMD combined: %{customdata[2]}<br>"
            "Difference (PPFI − IMD): %{customdata[3]}<br>"
            "%{customdata[4]}<br>"
            "%{customdata[5]}<br><br>"
            "<extra></extra>"
        )

    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson,
        locations="id",
        featureidkey="properties.id",
        color=color_col,
        range_color=range_color,
        color_continuous_scale=colorscale,
        opacity=0.85,
    )

    fig.update_traces(
        customdata=customdata,
        hovertemplate=hovertemplate,
        marker_line_width=0.3
    )

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=5.3,
            center={"lat": 53.7, "lon": -1.5},
        ),
        margin=dict(l=0,r=0,t=40,b=0),
        uirevision="keep",
        clickmode='event',
        coloraxis_colorbar=dict(
            title=colorbar_title,
            thickness=12,
            len=0.5,
        ),
    )

    return fig

def add_highlight_outline(fig, gdf, geojson, feature_id: str):
    return fig
