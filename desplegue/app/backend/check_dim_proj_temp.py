import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def check_dim_proyecto():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    df = pd.read_sql("SELECT * FROM dw.dim_proyecto LIMIT 1", engine)
    print("Columns:", df.columns.tolist())
    print("Data:", df.to_dict(orient='records'))

if __name__ == "__main__":
    check_dim_proyecto()
