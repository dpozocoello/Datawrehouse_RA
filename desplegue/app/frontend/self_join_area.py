import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def trace():
    query = """
    SELECT 
        child.nombre_area as area,
        parent.nombre_area as area_padre,
        child.zona,
        child.provincia,
        parent.zona as zona_padre,
        parent.provincia as provincia_padre
    FROM dw.dim_area child
    LEFT JOIN dw.dim_area parent ON child.id_area_padre = parent.id_area
    WHERE child.id_area_padre IS NOT NULL AND child.id_area_padre != 0
    LIMIT 30
    """
    df = pd.read_sql(query, engine)
    print(df.to_string())

    print("\n--- NODES matching Zonal/Provincial titles ---")
    query_titles = """
    SELECT nombre_area, zona, provincia 
    FROM dw.dim_area 
    WHERE nombre_area LIKE '%%ZONAL%%' OR nombre_area LIKE '%%PROVINCIAL%%'
    LIMIT 20
    """
    df_titles = pd.read_sql(query_titles, engine)
    print(df_titles.to_string())

if __name__ == "__main__":
    trace()
