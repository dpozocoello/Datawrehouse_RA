import pandas as pd
from sqlalchemy import create_engine, text
import sys

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def check_layers():
    engine = get_engine()
    
    print("--- 1. Samples from dw.fact_regularizacion.areas_protegidas ---")
    query1 = text("""
    SELECT areas_protegidas, COUNT(*) 
    FROM dw.fact_regularizacion 
    WHERE areas_protegidas IS NOT NULL AND areas_protegidas != '' AND areas_protegidas != 'NO'
    GROUP BY areas_protegidas 
    ORDER BY 2 DESC 
    LIMIT 20;
    """)
    try:
        df1 = pd.read_sql(query1, engine)
        print(df1.to_string())
    except Exception as e:
        print(f"Error checking fact_regularizacion: {e}")

    print("\n--- 2. Samples from dw.dim_capa_ambiental ---")
    query2 = text("SELECT * FROM dw.dim_capa_ambiental LIMIT 50;")
    try:
        df2 = pd.read_sql(query2, engine)
        print(df2.to_string())
    except Exception as e:
        print(f"Error checking dim_capa_ambiental: {e}")

if __name__ == "__main__":
    check_layers()
