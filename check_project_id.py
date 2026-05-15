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

print("--- Checking Project with Code LIKE %220472 in SUIA ---")
query_plc = "SELECT prco_id, prco_cua FROM coa_mae.project_licencing_coa WHERE prco_cua LIKE '%220472'"
df_plc = pd.read_sql(query_plc, engine_suia)
print(df_plc)

print("\n--- Checking Project with ID 220472 (if it exists under another table) ---")
# En el script de ingesta (waste_chemical.py) se usa coa_mae.project_licencing_coa
# Pero quiza el ID viene de otra tabla legacy?
query_pren = "SELECT pren_id, pren_code FROM suia_iii.projects_environmental_licensing WHERE pren_id = 220472"
try:
    df_pren = pd.read_sql(query_pren, engine_suia)
    print(df_pren)
except:
    print("suia_iii table not reachable or doesn't exist.")
