import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def find_zones():
    print("\n--- NODES matching 'ZONA' or 'ZONAL' ---")
    query = "SELECT id_area, nombre_area, id_area_padre, zona, provincia FROM dw.dim_area WHERE nombre_area iLIKE '%%ZONA%%'"
    df = pd.read_sql(query, engine)
    print(df.to_string())

    print("\n--- NODES matching 'PROVINCIAL' ---")
    query_p = "SELECT id_area, nombre_area, id_area_padre, zona, provincia FROM dw.dim_area WHERE nombre_area iLIKE '%%PROVINCIAL%%' LIMIT 20"
    df_p = pd.read_sql(query_p, engine)
    print(df_p.to_string())

if __name__ == "__main__":
    find_zones()
