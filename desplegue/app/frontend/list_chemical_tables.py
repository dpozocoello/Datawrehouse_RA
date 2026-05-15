from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Chemical Related Tables ---")
        query = text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE (table_schema IN ('dw', 'stg'))
              AND (table_name ILIKE '%chemical%' OR table_name ILIKE '%quimico%')
            ORDER BY table_schema, table_name
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
