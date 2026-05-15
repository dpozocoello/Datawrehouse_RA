import pandas as pd
from sqlalchemy import create_engine
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

try:
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    # Consultar columnas de la tabla RCOA
    query = "SELECT column_name FROM information_schema.columns WHERE table_schema = 'coa_mae' AND table_name = 'project_licencing_coa'"
    df = pd.read_sql(query, engine)
    print("### COLUMNS FOR coa_mae.project_licencing_coa ###")
    print(df['column_name'].tolist())
    
    # Consultar una fila de ejemplo para ver el formato de los códigos
    query_sample = "SELECT prco_id, prco_cua, prco_rgd_associated_code FROM coa_mae.project_licencing_coa WHERE prco_cua IS NOT NULL LIMIT 5"
    df_sample = pd.read_sql(query_sample, engine)
    print("\n### SAMPLE RCOA ROWS ###")
    print(df_sample.to_dict('records'))
except Exception as e:
    print(f"ERROR: {e}")
