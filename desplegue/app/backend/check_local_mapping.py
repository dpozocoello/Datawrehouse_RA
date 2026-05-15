import pandas as pd
from sqlalchemy import create_engine
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_DWH_LOCAL

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine = create_engine(build_uri(CONN_DWH_LOCAL))

print("--- Checking stg_project_mapping for suffix 220472 ---")
query = "SELECT * FROM stg.stg_project_mapping WHERE prco_cua LIKE '%220472'"
try:
    df = pd.read_sql(query, engine)
    print(df)
except Exception as e:
    print(f"Error: {e}")

print("\n--- Checking stg_fact_waste_generation records for that project ---")
query_f = "SELECT * FROM stg.stg_fact_waste_generation WHERE project_code LIKE '%220472'"
try:
    df_f = pd.read_sql(query_f, engine)
    print(df_f)
except Exception as e:
    print(f"Error: {e}")
