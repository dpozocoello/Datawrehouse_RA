from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Schema for stg.stg_chemical_sustances_records ---")
        query = text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'stg' AND table_name = 'stg_chemical_sustances_records'
            ORDER BY ordinal_position
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
