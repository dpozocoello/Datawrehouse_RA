from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Stored Procedures Related to Chemicals ---")
        query = text("""
            SELECT routine_schema, routine_name 
            FROM information_schema.routines 
            WHERE routine_schema IN ('dw', 'coa_mae', 'public')
              AND (routine_name ILIKE '%chemical%' OR routine_name ILIKE '%quimico%')
            ORDER BY routine_schema, routine_name
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
