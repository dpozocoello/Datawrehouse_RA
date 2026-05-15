import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def full_audit_lengths():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    
    tables = [
        "stg.stg_chemical_sustances_records",
        "stg.stg_import_request",
        "stg.stg_detail_import_request",
        "stg.stg_chemical_substances_declaration",
        "stg.stg_chemical_substances_movements"
    ]
    
    for table in tables:
        print(f"\n=== AUDIT: {table} ===")
        # Get all column names
        with engine.connect() as conn:
            res = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{table.split('.')[0]}' AND table_name = '{table.split('.')[-1]}'"))
            cols = [r[0] for r in res]
        
        # Check max length of each cast to text
        for c in cols:
            try:
                q = f"SELECT max(length(CAST({c} AS TEXT))) as max_len FROM {table}"
                df = pd.read_sql(q, engine)
                mlen = df.iloc[0]['max_len']
                if mlen is not None and mlen > 500:
                    print(f"!!! LARGE COLUMN: {c}: {mlen}")
                elif mlen is not None:
                    # just print something to show progress
                    pass 
            except Exception as e:
                print(f"Error {c}: {e}")
    print("\nDONE.")

if __name__ == "__main__":
    full_audit_lengths()
