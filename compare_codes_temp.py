import sys
import pandas as pd
from sqlalchemy import create_engine

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def compare_codes():
    uri = f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}"
    engine = create_engine(uri)
    
    q1 = "SELECT prco_cua FROM stg.stg_project_mapping WHERE prco_cua IS NOT NULL LIMIT 5"
    q2 = "SELECT codigo_proyecto FROM dw.dim_proyecto WHERE sk_proyecto != 0 LIMIT 5"
    
    res1 = pd.read_sql(q1, engine)
    res2 = pd.read_sql(q2, engine)
    
    print("STG Mapping CUA:", res1['prco_cua'].tolist())
    print("DW Dim Proyecto Code:", res2['codigo_proyecto'].tolist())

if __name__ == "__main__":
    compare_codes()
