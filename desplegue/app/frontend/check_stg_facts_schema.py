from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        'stg_chemical_substances_declaration',
        'stg_chemical_substances_movements'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            print(f"--- Schema for stg.{table} ---")
            query = text(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'stg' AND table_name = '{table}'
                ORDER BY ordinal_position
            """)
            df = pd.read_sql(query, conn)
            print(df.to_string())
            print("\n")
            
except Exception as e:
    print(f"Error: {e}")
