import json
import pandas as pd
from sqlalchemy import create_engine
import unicodedata

def normalize(s):
    if not s: return ""
    return "".join(
        c for c in unicodedata.normalize('NFD', str(s).upper())
        if unicodedata.category(c) != 'Mn'
    ).strip()

# DB Config
conn_str = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8"
engine = create_engine(conn_str)

print("--- DIAGNOSTICO DE DATOS GEOGRAFICOS ---")

# 1. Check DB Values
df_db = pd.read_sql("SELECT DISTINCT provincia, canton FROM dw.dim_geografia", engine)
db_provincias = sorted(df_db['provincia'].unique())
db_cantones = sorted(df_db['canton'].unique())
print(f"DB Provincias ({len(db_provincias)}): {db_provincias[:5]}...")
print(f"DB Cantones ({len(db_cantones)}): {db_cantones[:5]}...")

# 2. Check Provincias GeoJSON
try:
    with open('d:/DashboardRA/ecuador_provincias.geojson', 'r', encoding='utf-8') as f:
        geo_prov = json.load(f)
    props_prov = geo_prov['features'][0]['properties']
    print("\n[PROVINCIAS GEOJSON]")
    print("Properties available:", list(props_prov.keys()))
    geojson_prov_names = sorted([f['properties'].get('provincia') for f in geo_prov['features'] if f['properties'].get('provincia')])
    print(f"GeoJSON Sample Names (KEY 'provincia'): {geojson_prov_names[:5]}...")
    
    # Check match
    matches = [p for p in db_provincias if normalize(p) in [normalize(gp) for gp in geojson_prov_names]]
    print(f"Match Rate (Database vs GeoJSON): {len(matches)}/{len(db_provincias)}")
except Exception as e:
    print(f"Error in Provincias GeoJSON: {e}")

# 3. Check Cantones GeoJSON
try:
    with open('d:/DashboardRA/ecuador_cantones.geojson', 'r', encoding='utf-8') as f:
        geo_cant = json.load(f)
    props_cant = geo_cant['features'][0]['properties']
    print("\n[CANTONES GEOJSON]")
    print("Properties available:", list(props_cant.keys()))
    geojson_cant_names = sorted([f['properties'].get('canton') for f in geo_cant['features'] if f['properties'].get('canton')])
    print(f"GeoJSON Sample Names (KEY 'canton'): {geojson_cant_names[:5]}...")
    
    # Check match
    matches_c = [c for c in db_cantones if normalize(c) in [normalize(gc) for gc in geojson_cant_names]]
    print(f"Match Rate (Database vs GeoJSON): {len(matches_c)}/{len(db_cantones)}")
except Exception as e:
    print(f"Error in Cantones GeoJSON: {e}")
