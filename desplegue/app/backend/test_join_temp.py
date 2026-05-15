import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def test_join():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    
    query = """
    SELECT 
        COALESCE(dp.sk_proyecto, 0),
        COALESCE(ds.chemical_key, 0),
        COALESCE(di.importer_key, 0),
        COALESCE(dt.sk_tiempo, 0),
        dr.deir_available_space
    FROM stg.stg_import_request ir
    JOIN stg.stg_detail_import_request dr ON ir.inre_id = dr.inre_id
    LEFT JOIN stg.stg_chemical_sustances_records rec ON ir.chsr_id = rec.chsr_id
    LEFT JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = (
        SELECT prco_cua FROM coa_mae.project_licencing_coa WHERE prco_id = rec.prco_id LIMIT 1
    )
    LIMIT 10
    """
    
    print("Testing Join Query...")
    try:
        df = pd.read_sql(query, engine)
        print("Join Query SUCCESS.")
        print(df.to_string())
    except Exception as e:
        print(f"Join Query FAILED: {e}")

if __name__ == "__main__":
    test_join()
