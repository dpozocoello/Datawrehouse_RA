from sqlalchemy import create_engine, text
import pandas as pd
import requests

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
with engine.connect() as conn:
    q = text("SELECT DISTINCT provincia FROM dw.dim_geografia ORDER BY 1")
    db_provinces = pd.read_sql(q, conn)['provincia'].tolist()

repo_url = "https://raw.githubusercontent.com/jpmarindiaz/geo-collection/master/ecu/ecuador.geojson"
data = requests.get(repo_url).json()
geojson_provinces = sorted(list(set([f['properties']['dpa_despro'] for f in data['features']])))

with open('f:/DashboardRA/proc_mapping.txt', 'w', encoding='utf-8') as f:
    f.write("--- DB PROVINCES ---\n")
    f.write('\n'.join(db_provinces) + "\n")
    f.write("\n--- GEOJSON PROVINCES ---\n")
    f.write('\n'.join(geojson_provinces) + "\n")

print("Mapping written to f:/DashboardRA/proc_mapping.txt")
