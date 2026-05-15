import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def check_populated_parents():
    print("\n--- ZONAL nodes data ---")
    query_z = "SELECT id_area, nombre_area, zona, provincia FROM dw.dim_area WHERE nombre_area iLIKE '%%ZONAL%%' OR nombre_area iLIKE '%%DIRECCION ZONAL%%'"
    df_z = pd.read_sql(query_z, engine)
    print(df_z.to_string())

    print("\n--- PROVINCIAL nodes data ---")
    query_p = "SELECT id_area, nombre_area, zona, provincia FROM dw.dim_area WHERE nombre_area iLIKE '%%PROVINCIAL%%' OR nombre_area iLIKE '%%DIRECCION PROVINCIAL%%'"
    df_p = pd.read_sql(query_p, engine)
    print(df_p.to_string())

if __name__ == "__main__":
    check_populated_parents()
