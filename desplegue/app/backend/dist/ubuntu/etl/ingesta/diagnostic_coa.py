import pandas as pd
from sqlalchemy import create_engine
import sys
import os

sys.path.insert(0, r'/opt/eco-sieaa/etl')
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

try:
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    # Consultar columnas de la tabla de datos generales
    target_table = 'hazardous_wastes_waste_dangerous_general_data'
    df_hw = pd.read_sql(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'suia_iii' AND table_name = '{target_table}'", engine)
    print(f"/n### COLUMNS FOR suia_iii.{target_table} ###")
    print(df_hw)
    
    # Consultar una fila de detalle
    try:
        df_sample_det = pd.read_sql(f"SELECT * FROM suia_iii.{target_table} LIMIT 1", engine)
        print("/n### SAMPLE DETAIL ROW ###")
        print(df_sample_det.iloc[0].to_dict() if not df_sample_det.empty else "No rows found")
    except Exception as e:
        print(f"Error sampling {target_table}: {e}")
    
    # Consultar una fila para ver ejemplos
    df_sample = pd.read_sql("SELECT * FROM suia_iii.hazardous_wastes_generators LIMIT 1", engine)
    print("/n### SAMPLE ROW ###")
    print(df_sample.iloc[0].to_dict() if not df_sample.empty else "No rows found")
    
except Exception as e:
    print(f"ERROR: {e}")
