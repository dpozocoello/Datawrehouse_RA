import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def check_local_lengths():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    
    table = "stg.stg_chemical_substances_movements"
    
    # Get all column names first
    with engine.connect() as conn:
        res = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'stg' AND table_name = '{table.split('.')[-1]}'"))
        cols = [r[0] for r in res]
    
    print(f"=== {table} LENGTH AUDIT ===")
    for c in cols:
        try:
            # Only check text-like columns
            res = pd.read_sql(f"SELECT '{c}' as column, max(length(CAST({c} AS TEXT))) as max_len FROM {table}", engine)
            print(f"{res.iloc[0]['column']}: {res.iloc[0]['max_len']}")
        except Exception as e:
            print(f"{c}: Error {e}")

if __name__ == "__main__":
    check_local_lengths()
