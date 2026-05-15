import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def check_more_raw():
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    
    tables = [
        "coa_chemical_sustances.chemical_substances_declaration",
        "coa_chemical_sustances.chemical_substances_movements"
    ]
    
    print("=== MORE RAW DATA CHECK ===")
    for t in tables:
        try:
            res = pd.read_sql(f"SELECT count(*) as count FROM {t}", engine)
            print(f"{t}: {res.iloc[0]['count']}")
        except Exception as e:
            print(f"{t}: Error {e}")
    print("==========================")

if __name__ == "__main__":
    check_more_raw()
