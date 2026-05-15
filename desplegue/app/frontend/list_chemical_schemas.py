from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        'dw.dim_chemical_importer',
        'dw.dim_chemical_storage',
        'dw.dim_chemical_substance',
        'dw.fact_chemical_application',
        'dw.fact_chemical_declaration',
        'dw.fact_chemical_import',
        'dw.fact_chemical_movement'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            schema, name = table.split('.')
            print(f"--- Schema for {table} ---")
            query = text(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = '{schema}' AND table_name = '{name}'
                ORDER BY ordinal_position
            """)
            df = pd.read_sql(query, conn)
            print(df.to_string())
            print("\n")
            
except Exception as e:
    print(f"Error: {e}")
