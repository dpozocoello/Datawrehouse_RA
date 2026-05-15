import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def list_dwh_schemas():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    query = "SELECT nspname FROM pg_namespace WHERE nspname NOT LIKE 'pg_%%' AND nspname != 'information_schema'"
    df = pd.read_sql(query, engine)
    print(df.to_string(index=False))

if __name__ == "__main__":
    list_dwh_schemas()
