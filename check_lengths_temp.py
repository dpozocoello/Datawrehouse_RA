import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def check_lengths():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    
    checks = {
        "chsr_name_rep_legal": "SELECT max(length(chsr_name_rep_legal)) FROM stg.stg_chemical_sustances_records",
        "chsm_operator": "SELECT max(length(chsm_operator)) FROM stg.stg_chemical_substances_movements",
        "inre_document_autorizes": "SELECT max(length(inre_document_autorizes)) FROM stg.stg_import_request"
    }
    
    print("=== COLUMN LENGTH AUDIT ===")
    for name, query in checks.items():
        try:
            res = pd.read_sql(query, engine)
            print(f"{name}: {res.iloc[0][0]}")
        except Exception as e:
            print(f"{name}: Error {e}")

if __name__ == "__main__":
    check_lengths()
