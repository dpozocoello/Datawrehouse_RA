from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        ('stg', 'stg_import_request'),
        ('stg', 'stg_detail_import_request')
    ]
    
    with engine.connect() as conn:
        for schema, table in tables:
            print(f"--- Schema for {schema}.{table} ---")
            query = text(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = '{schema}' AND table_name = '{table}'
                ORDER BY ordinal_position
            """)
            df = pd.read_sql(query, conn)
            print(df.to_string())
            print("\n")
            
except Exception as e:
    print(f"Error: {e}")
