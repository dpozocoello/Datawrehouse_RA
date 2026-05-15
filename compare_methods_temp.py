import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def compare_methods():
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    
    table = "coa_chemical_sustances.chemical_substances_movements"
    
    # Method 1: Count
    res_count = pd.read_sql(f"SELECT count(*) FROM {table}", engine)
    print(f"COUNT Query: {res_count.iloc[0][0]}")
    
    # Method 2: Select columns (from ingesta script)
    query_ingesta = """
        SELECT chsm_id, chsd_id, chsm_invoice, chsm_operator, chsm_entry, chsm_exit, achs_id
        FROM coa_chemical_sustances.chemical_substances_movements
    """
    df_cols = pd.read_sql(query_ingesta, engine)
    print(f"COLS Query Shape: {df_cols.shape}")

if __name__ == "__main__":
    compare_methods()
