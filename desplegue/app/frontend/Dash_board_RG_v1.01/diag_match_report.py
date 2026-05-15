import json
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

with open("d:/DashboardRA/ecuador_provincias.geojson", encoding='utf-8') as f:
    geo = json.load(f)

geo_names = [feat['properties'].get('provincia', '') for feat in geo['features']]
geo_upper = {n.upper(): n for n in geo_names}

# DB names
df = pd.read_sql("SELECT DISTINCT provincia FROM dw.dim_geografia ORDER BY provincia", engine)
db_names = df['provincia'].tolist()

print("=== MATCH REPORT ===")
matched = 0
unmatched_db = []
for name in db_names:
    up = name.upper() if name else ''
    if up in geo_upper:
        matched += 1
    else:
        unmatched_db.append(name)

print(f"Matched: {matched}/{len(db_names)}")
print(f"Unmatched DB names: {unmatched_db}")
print(f"\nGeoJSON names: {geo_names}")
print(f"\nDB names (upper): {[n.upper() for n in db_names if n]}")
