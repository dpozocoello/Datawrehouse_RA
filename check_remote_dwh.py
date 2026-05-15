import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# Try to connect to .226 as DWH
def check_remote_dwh():
    uri = "postgresql://postgres:postgres@172.16.0.226:5432/dw_reg_v1"
    try:
        engine = create_engine(uri)
        res = pd.read_sql("SELECT count(*) FROM dw.dim_proyecto", engine)
        print(f"SUCCESS: Connected to .226 DWH. Project Count: {res.iloc[0][0]}")
    except Exception as e:
        print(f"FAILED: Connection to .226 DWH failed: {e}")

if __name__ == "__main__":
    check_remote_dwh()
