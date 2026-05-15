import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:postgres@localhost:5432/ECO_SIEAA')

try:
    cols_proy = list(pd.read_sql('SELECT * FROM dw.dim_proyecto LIMIT 1', engine).columns)
    print("Columnas en dim_proyecto:", cols_proy)
    
    unique_estados = pd.read_sql('SELECT DISTINCT estado_proyecto FROM dw.dim_estado', engine)
    print("Valores unicos de estado_proyecto en dim_estado:")
    print(unique_estados)
    
    unique_proceso = pd.read_sql('SELECT DISTINCT estado_proceso FROM dw.dim_estado', engine)
    print("Valores unicos de estado_proceso en dim_estado:")
    print(unique_proceso)
except Exception as e:
    print("Error:", e)
