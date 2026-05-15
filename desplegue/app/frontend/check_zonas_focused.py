import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def inspect():
    print("\n--- DISTINCT ZONAS in dim_area ---")
    df_z = pd.read_sql("SELECT zona, COUNT(*) as count FROM dw.dim_area GROUP BY zona", engine)
    print(df_z.to_string())

    print("\n--- SAMPLE: dim_area where zona != 'N/A' ---")
    df_s = pd.read_sql("SELECT nombre_area, zona, provincia, canton, parroquia FROM dw.dim_area WHERE zona != 'N/A' LIMIT 20", engine)
    print(df_s.to_string())

    print("\n--- SAMPLE: dim_area where zona == 'N/A' ---")
    df_na = pd.read_sql("SELECT nombre_area, zona, provincia, canton, parroquia FROM dw.dim_area WHERE zona = 'N/A' LIMIT 10", engine)
    print(df_na.to_string())

if __name__ == "__main__":
    inspect()
