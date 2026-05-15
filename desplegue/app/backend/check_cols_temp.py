import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def check_columns():
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    
    tables = [
        "coa_chemical_sustances.chemical_substances_declaration",
        "coa_chemical_sustances.chemical_substances_movements"
    ]
    
    for t in tables:
        try:
            print(f"\n--- {t} ---")
            df = pd.read_sql(f"SELECT * FROM {t} LIMIT 1", engine)
            print(f"Columns: {df.columns.tolist()}")
            print(f"Data: {df.to_dict(orient='records')}")
        except Exception as e:
            print(f"Error checking {t}: {e}")

if __name__ == "__main__":
    check_columns()
