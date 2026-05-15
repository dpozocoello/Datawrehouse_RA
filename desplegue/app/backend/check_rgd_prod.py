import pandas as pd
from sqlalchemy import create_engine
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_SUIA_ENLISY

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine_suia = create_engine(build_uri(CONN_SUIA_ENLISY))

print("--- Checking RGD in SUIA PRODUCTION ---")
# Buscamos el ware_id para el codigo dado
query_rgd = "SELECT ware_id, ware_code, ware_status FROM coa_waste_generator_record.waste_generator_record_coa WHERE ware_code = 'MAATE-SOL-RGD-2024-10623'"
df_rgd = pd.read_sql(query_rgd, engine_suia)
print(df_rgd)

if not df_rgd.empty:
    ware_id = df_rgd.iloc[0]['ware_id']
    print(f"\n--- Checking Projects linked to ware_id {ware_id} in LP table ---")
    query_lp = f"SELECT * FROM coa_waste_generator_record.waste_generator_record_project_licencing_coa WHERE ware_id = {ware_id}"
    df_lp = pd.read_sql(query_lp, engine_suia)
    print(df_lp)
    
    if not df_lp.empty:
        prco_ids = df_lp['id_proyect'].tolist()
        prco_ids_str = ",".join([str(i) for i in prco_ids if i is not None])
        if prco_ids_str:
            print(f"\n--- Checking Project Codes for prco_ids ({prco_ids_str}) ---")
            query_plc = f"SELECT prco_id, prco_cua FROM coa_mae.project_licencing_coa WHERE prco_id IN ({prco_ids_str})"
            df_plc = pd.read_sql(query_plc, engine_suia)
            print(df_plc)
        else:
            print("\nNo direct id_proyect found in lp table.")
else:
    print("\nRGD not found in production with that code.")
