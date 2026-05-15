import json
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

# 1. GeoJSON province keys
with open("d:/DashboardRA/ecuador_provincias.geojson", encoding='utf-8') as f:
    prov_geo = json.load(f)

feat0 = prov_geo['features'][0]
print("=== PROVINCIAS GEOJSON ===")
print(f"Keys: {list(feat0['properties'].keys())}")
for i in range(min(5, len(prov_geo['features']))):
    props = prov_geo['features'][i]['properties']
    print(f"  Feature {i}: {props}")

# 2. GeoJSON canton keys  
with open("d:/DashboardRA/ecuador_cantones.geojson", encoding='utf-8') as f:
    cant_geo = json.load(f)

feat0c = cant_geo['features'][0]
print("\n=== CANTONES GEOJSON ===")
print(f"Keys: {list(feat0c['properties'].keys())}")
for i in range(min(5, len(cant_geo['features']))):
    props = cant_geo['features'][i]['properties']
    print(f"  Feature {i}: {props}")

# 3. DB province names
print("\n=== DB PROVINCIA NAMES (sample) ===")
df = pd.read_sql("SELECT DISTINCT provincia FROM dw.dim_geografia ORDER BY provincia LIMIT 10", engine)
print(df.to_string())
