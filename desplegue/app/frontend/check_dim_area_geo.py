import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def inspect():
    print("\n--- POPULATION of geographic columns in dim_area ---")
    query = """
    SELECT 
        COUNT(*) as total,
        COUNT(provincia) as has_prov,
        COUNT(canton) as has_canton,
        COUNT(parroquia) as has_parroquia,
        COUNT(zona) as has_zona
    FROM dw.dim_area
    """
    df = pd.read_sql(query, engine)
    print(df.to_string())

    print("\n--- DISTINCT Provincias in dim_area ---")
    df_p = pd.read_sql("SELECT provincia, COUNT(*) as count FROM dw.dim_area GROUP BY provincia", engine)
    print(df_p.to_string())

if __name__ == "__main__":
    inspect()
