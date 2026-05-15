
import json
import unicodedata
import pandas as pd
from sqlalchemy import create_engine, text

def normalize_name(name):
    if not name: return ""
    name = str(name)
    name = unicodedata.normalize('NFD', name)
    name = "".join([c for c in name if unicodedata.category(c) != 'Mn'])
    return name.upper().strip()

# Database config
CONN_STR = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8"
engine = create_engine(CONN_STR)

# Load data from DB
query = text("""
    SELECT DISTINCT geo.provincia as ubicacion
    FROM dw.dim_geografia geo
    WHERE geo.provincia IS NOT NULL
""")
df_db = pd.read_sql(query, engine)
df_db['norm'] = df_db['ubicacion'].apply(normalize_name)

# Load GeoJSON
geojson_file = r"D:\DashboardRA\Dash_board_RG_v1.01\ecuador_provincias.geojson"
with open(geojson_file, encoding='utf-8') as f:
    geojson_data = json.load(f)

print(f"--- Comparison for PROVINCIAS ---")
geojson_names = []
for feature in geojson_data['features']:
    props = feature['properties']
    # Try multiple keys
    for key in ['provincia', 'provincia'.lower(), 'provincia'.capitalize(), 'NAME', 'name']:
        if key in props:
            geojson_names.append(props[key])
            break

df_geo = pd.DataFrame({'raw': geojson_names})
df_geo['norm'] = df_geo['raw'].apply(normalize_name)

print(f"DB Norm Names (first 10): {df_db['norm'].head(10).tolist()}")
print(f"GeoJSON Norm Names (first 10): {df_geo['norm'].head(10).tolist()}")

# Check intersection
db_set = set(df_db['norm'])
geo_set = set(df_geo['norm'])

missing_in_geo = db_set - geo_set
missing_in_db = geo_set - db_set

print(f"\nMissing in GeoJSON: {missing_in_geo}")
print(f"Missing in DB: {missing_in_db}")
print(f"Match count: {len(db_set & geo_set)} / {len(db_set)}")
