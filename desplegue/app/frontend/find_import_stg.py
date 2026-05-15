from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Staging tables related to chemical imports ---")
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'stg' 
            AND table_name LIKE '%import%'
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
