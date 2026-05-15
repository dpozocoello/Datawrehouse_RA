import json
import unicodedata
import pandas as pd
from sqlalchemy import create_engine

def normalize_name(name):
    if not name: return ""
    return "".join(
        c for c in unicodedata.normalize('NFD', str(name).upper())
        if unicodedata.category(c) != 'Mn'
    ).strip()

def diag():
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
    
    # Check Provincias
    print("--- PROVINCIAS ---")
    df_db = pd.read_sql("SELECT DISTINCT provincia FROM dw.dim_geografia WHERE provincia IS NOT NULL", engine)
    db_names = set(df_db['provincia'].apply(normalize_name))
    
    with open(r"d:\DashboardRA\Dash_board_RG_v1.01\ecuador_provincias.geojson", encoding='utf-8') as f:
        geojson = json.load(f)
    
    geo_names = []
    for feature in geojson['features']:
        val = None
        for key in ['provincia', 'name', 'NAME']:
            if key in feature['properties']:
                val = feature['properties'][key]
                break
        if val:
            geo_names.append(normalize_name(str(val)))
    
    geo_names_set = set(geo_names)
    
    print(f"DB Normalize Names: {sorted(list(db_names))[:5]}... (Total: {len(db_names)})")
    print(f"GeoJSON Normalize Names: {sorted(list(geo_names_set))[:5]}... (Total: {len(geo_names_set)})")
    
    missing_in_geo = db_names - geo_names_set
    print(f"Missing in GeoJSON: {missing_in_geo}")
    
    # Check Cantones
    print("\n--- CANTONES ---")
    df_db_c = pd.read_sql("SELECT DISTINCT canton FROM dw.dim_geografia WHERE canton IS NOT NULL LIMIT 20", engine)
    db_names_c = set(df_db_c['canton'].apply(normalize_name))
    print(f"Sample DB Cantones: {db_names_c}")

if __name__ == "__main__":
    diag()
