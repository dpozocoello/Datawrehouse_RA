import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def check_col_counts():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    tables = [
        "stg.stg_chemical_sustances_records",
        "stg.stg_import_request",
        "stg.stg_detail_import_request",
        "stg.stg_chemical_substances_declaration",
        "stg.stg_chemical_substances_movements"
    ]
    for t in tables:
        df = pd.read_sql(f"SELECT * FROM {t} LIMIT 0", engine)
        print(f"{t}: {len(df.columns)} columns")

if __name__ == "__main__":
    check_col_counts()
