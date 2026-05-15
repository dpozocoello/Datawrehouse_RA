import json
import pandas as pd
from sqlalchemy import create_engine

# Configuration
GEOJSON_PROV = "d:/DashboardRA/ecuador_provincias.geojson"
GEOJSON_CANT = "d:/DashboardRA/ecuador_cantones.geojson"
DB_URL = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
engine = create_engine(DB_URL)

def diag_geo_names():
    print("--- DIAGNÓSTICO DE NOMBRES GIS ---")
    
    # 1. Load GeoJSON names
    with open(GEOJSON_PROV, encoding='utf-8') as f:
        provincias_geo = [feat['properties']['name'] for feat in json.load(f)['features']]
    
    with open(GEOJSON_CANT, encoding='utf-8') as f:
        cantones_geo = [feat['properties']['name'] for feat in json.load(f)['features']]
        
    # 2. Load DB names
    with engine.connect() as conn:
        df_db = pd.read_sql("SELECT DISTINCT provincia, canton FROM dw.dim_geografia", conn)
    
    prov_db = df_db['provincia'].unique()
    cant_db = df_db['canton'].unique()
    
    # 3. Compare Provinces
    miss_prov = [p for p in prov_db if p not in provincias_geo and p != 'N/A' and p != 'TODAS']
    print(f"Provincias en DB NO encontradas en GeoJSON: {miss_prov}")
    print(f"Total Provincias GeoJSON: {len(provincias_geo)}")
    
    # 4. Compare Cantons
    miss_cant = [c for c in cant_db if c not in cantones_geo and c != 'N/A' and c != 'TODOS']
    print(f"Total Cantones en DB desalineados: {len(miss_cant)} (Primeros 10: {miss_cant[:10]})")
    print(f"Total Cantones GeoJSON: {len(cantones_geo)}")

if __name__ == "__main__":
    diag_geo_names()
