# utils/data_loader.py

import json
import pandas as pd
import geopandas as gpd


def load_all_data():
    # read files
    gdf_lsoa = gpd.read_file('data/ppfi_imd_lsoa_england.geojson')
    gdf_lad  = gpd.read_file('data/ppfi_imd_lad_england.geojson')

    df_mismatch = pd.read_csv('data/imd_ppfi_mismatch.csv')

    # fix crs for it to work with plotly
    gdf_lsoa = gdf_lsoa.set_crs(27700, allow_override=True).to_crs(4326)
    gdf_lad  = gdf_lad.set_crs(27700, allow_override=True).to_crs(4326)

    # normalise keys (strip whitespace, force uppercase)
    gdf_lsoa = gdf_lsoa.copy()
    df_mismatch = df_mismatch.copy()

    gdf_lsoa['LSOA21CD'] = gdf_lsoa['LSOA21CD'].astype(str).str.strip().str.upper()
    df_mismatch['lsoa21cd'] = df_mismatch['lsoa21cd'].astype(str).str.strip().str.upper()
    df_mismatch['lad24cd'] = df_mismatch['lad24cd'].astype(str).str.strip().str.upper()

    lsoa_to_lad = (
        df_mismatch[['lsoa21cd', 'lad24cd']]
        .dropna(subset=['lsoa21cd', 'lad24cd'])
        .drop_duplicates(subset=['lsoa21cd'])
        .rename(columns={'lsoa21cd': 'LSOA21CD', 'lad24cd': 'lad_cd'})
    )

    gdf_lsoa = gdf_lsoa.merge(lsoa_to_lad, on='LSOA21CD', how='left')

    # numeric coercion
    for col in gdf_lsoa.columns:
        if col.startswith(('pp_', 'imd_')):
            gdf_lsoa[col] = pd.to_numeric(gdf_lsoa[col], errors='coerce')

    for col in gdf_lad.columns:
        if col.startswith(('combined', 'domain_', 'imd_', 'income_', 'employment_',
                           'education_', 'health_', 'crime_', 'barriers_', 'living_')):
            gdf_lad[col] = pd.to_numeric(gdf_lad[col], errors='coerce')

    # add id columns for plotly (must match geojson properties.id)
    gdf_lsoa['id'] = gdf_lsoa['LSOA21CD'].astype(str)
    gdf_lad['id'] = gdf_lad['LAD24CD'].astype(str).str.strip().str.upper()

    # convert to json
    geojson_lsoa = json.loads(gdf_lsoa.to_json(drop_id=True))
    geojson_lad  = json.loads(gdf_lad.to_json(drop_id=True))

    # sanity checking
    assert set(gdf_lsoa['id']) == {f['properties']['id'] for f in geojson_lsoa['features']}
    assert set(gdf_lad['id'])  == {f['properties']['id'] for f in geojson_lad['features']}

    # mismatch prep
    df_mismatch['abs_diff'] = df_mismatch['ppfi_imd_diff'].abs()
    df_mismatch.sort_values('abs_diff', ascending=False, inplace=True)

    # join ward names
    try:
        ward_lookup = pd.read_csv('data/lsoa21_ward_lookup.csv')
        ward_col = next((c for c in ward_lookup.columns if 'LSOA' in c.upper()), None)
        name_col = next((c for c in ward_lookup.columns if 'WD' in c.upper() and 'NM' in c.upper()), None)
        if ward_col and name_col:
            ward_lookup = (
                ward_lookup[[ward_col, name_col]]
                .rename(columns={ward_col: '_lsoa_key', name_col: 'ward_name'})
            )
            ward_lookup['_lsoa_key'] = ward_lookup['_lsoa_key'].astype(str).str.strip().str.upper()
            ward_lookup = ward_lookup.drop_duplicates('_lsoa_key')
            df_mismatch = df_mismatch.merge(
                ward_lookup, left_on='lsoa21cd', right_on='_lsoa_key', how='left'
            ).drop(columns=['_lsoa_key'])
    except FileNotFoundError:
        df_mismatch['ward_name'] = ''

    return gdf_lsoa, geojson_lsoa, gdf_lad, geojson_lad, df_mismatch
