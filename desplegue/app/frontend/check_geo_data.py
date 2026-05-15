import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def inspect():
    with engine.connect() as conn:
        print("\n--- COLUMNS: dim_area ---")
        df = pd.read_sql("SELECT * FROM dw.dim_area LIMIT 0", engine)
        print(df.columns.tolist())
        
        print("\n--- SAMPLE: dim_area (distinct zona) ---")
        df_z = pd.read_sql("SELECT DISTINCT zona FROM dw.dim_area", engine)
        print(df_z)

        print("\n--- SAMPLE: dim_area (nombre_area, zona, provincia) ---")
        df_s = pd.read_sql("SELECT nombre_area, zona, provincia, canton, parroquia FROM dw.dim_area LIMIT 10", engine)
        print(df_s.to_string())

        print("\n--- COLUMNS: dim_geografia ---")
        df_g = pd.read_sql("SELECT * FROM dw.dim_geografia LIMIT 0", engine)
        print(df_g.columns.tolist())

        print("\n--- SAMPLE: dim_geografia (provincia, canton, parroquia) ---")
        df_gs = pd.read_sql("SELECT provincia, canton, parroquia FROM dw.dim_geografia LIMIT 10", engine)
        print(df_gs.to_string())

if __name__ == "__main__":
    inspect()
