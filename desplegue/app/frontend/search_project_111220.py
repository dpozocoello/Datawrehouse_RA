from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Searching for project with code 111220 ---")
        query = text("""
            SELECT sk_proyecto, codigo_proyecto 
            FROM dw.dim_proyecto 
            WHERE codigo_proyecto LIKE '%111220%'
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
