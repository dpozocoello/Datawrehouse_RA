import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def inspect():
    print("\n--- SCHEMA: fact_proyecto_geografia ---")
    df_schema = pd.read_sql("SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'fact_proyecto_geografia'", engine)
    print(df_schema['column_name'].tolist())

    print("\n--- DATA: fact_proyecto_geografia ---")
    df_data = pd.read_sql("SELECT * FROM dw.fact_proyecto_geografia LIMIT 10", engine)
    print(df_data.to_string())

    print("\n--- RECURSIVE CHECK: dim_area TOP NODES names ---")
    df_top = pd.read_sql("SELECT nombre_area, zona, provincia FROM dw.dim_area WHERE id_area_padre IS NULL OR id_area_padre = 0", engine)
    print(df_top.to_string())

if __name__ == "__main__":
    inspect()
