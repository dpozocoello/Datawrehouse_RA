import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def inspect():
    print("\n--- DETAILED POPULATION: dim_area ---")
    query = """
    SELECT 
        COUNT(*) as total_rows,
        SUM(CASE WHEN provincia IS NOT NULL AND provincia != '' AND provincia != 'N/A' THEN 1 ELSE 0 END) as has_provincia,
        SUM(CASE WHEN canton IS NOT NULL AND canton != '' AND canton != 'N/A' THEN 1 ELSE 0 END) as has_canton,
        SUM(CASE WHEN parroquia IS NOT NULL AND parroquia != '' AND parroquia != 'N/A' THEN 1 ELSE 0 END) as has_parroquia,
        SUM(CASE WHEN zona IS NOT NULL AND zona != '' AND zona != 'N/A' THEN 1 ELSE 0 END) as has_zona
    FROM dw.dim_area
    """
    df = pd.read_sql(query, engine)
    print(df.to_string())

    print("\n--- SAMPLE of populated rows in dim_area ---")
    query_sample = """
    SELECT nombre_area, zona, provincia, canton, parroquia 
    FROM dw.dim_area 
    WHERE provincia IS NOT NULL AND provincia != '' AND provincia != 'N/A'
    LIMIT 20
    """
    df_sample = pd.read_sql(query_sample, engine)
    print(df_sample.to_string())

if __name__ == "__main__":
    inspect()
