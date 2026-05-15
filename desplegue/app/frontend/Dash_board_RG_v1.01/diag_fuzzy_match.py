import json
import pandas as pd
from sqlalchemy import create_engine
import unicodedata

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

with open("d:/DashboardRA/ecuador_provincias.geojson", encoding='utf-8') as f:
    geo = json.load(f)

def normalize(s):
    """Remove accents and convert to uppercase for fuzzy matching"""
    if not s: return ''
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).upper()

geo_names = [feat['properties'].get('provincia', '') for feat in geo['features']]
# Build lookup: normalized -> original GeoJSON name
geo_norm = {normalize(n): n for n in geo_names}

df = pd.read_sql("SELECT DISTINCT provincia FROM dw.dim_geografia ORDER BY provincia", engine)

print("=== FUZZY MATCH WITH NORMALIZATION ===")
for _, row in df.iterrows():
    db_name = row['provincia']
    db_norm = normalize(db_name)
    geo_match = geo_norm.get(db_norm, 'NO MATCH')
    status = '✓' if geo_match != 'NO MATCH' else '✗'
    if geo_match == 'NO MATCH':
        print(f"  {status} DB: '{db_name}' -> norm: '{db_norm}' -> NO MATCH")

print(f"\nGeoJSON normalized names: {list(geo_norm.keys())}")
