from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Searching for substance with chemical_id 163 ---")
        query = text("""
            SELECT chemical_key, substance_name 
            FROM dw.dim_chemical_substance 
            WHERE chemical_id = 163
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
