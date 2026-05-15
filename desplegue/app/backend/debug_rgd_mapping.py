import pandas as pd
from sqlalchemy import create_engine
import sys
import os

# CONFIG DIRECTO PARA EVITAR PROBLEMAS DE IMPORT
CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password", # Asumiendo el estandar si no lo veo
    "database": "dwh_bi"
}

# Pero mejor intentamos leerlo de config.py si podemos
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
    from config import CONN_DWH_LOCAL
except Exception as e:
    print(f"No se pudo cargar config, usando defaults: {e}")

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine = create_engine(build_uri(CONN_DWH_LOCAL))

print("--- Checking stg_fact_waste_generation for project codes ending in 220472 ---")
query = """
SELECT project_code, waste_generator_id, source_system, count(*) 
FROM stg.stg_fact_waste_generation 
WHERE project_code LIKE '%220472'
GROUP BY 1, 2, 3
"""
try:
    df = pd.read_sql(query, engine)
    print(df)
except Exception as e:
    print(f"Error en consulta 1: {e}")

print("\n--- Checking dim_waste_generator for related IDs ---")
query_gen = "SELECT waste_generator_id, generator_name, ruc_generator FROM dw.dim_waste_generator WHERE waste_generator_id IN (SELECT DISTINCT waste_generator_id FROM stg.stg_fact_waste_generation WHERE project_code LIKE '%220472')"
try:
    df_gen = pd.read_sql(query_gen, engine)
    print(df_gen)
except Exception as e:
    print(f"Error en consulta 2: {e}")

print("\n--- Checking dim_proyecto for code 220472 ---")
query_proj = "SELECT sk_proyecto, codigo_proyecto FROM dw.dim_proyecto WHERE codigo_proyecto LIKE '%220472'"
try:
    df_proj = pd.read_sql(query_proj, engine)
    print(df_proj)
except Exception as e:
    print(f"Error en consulta 3: {e}")
