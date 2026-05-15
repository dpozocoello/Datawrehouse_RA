from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        'dw.dim_chemical_importer',
        'dw.fact_chemical_import',
        'dw.fact_chemical_movement',
        'dw.fact_chemical_declaration'
    ]
    
    with engine.connect() as conn:
        print("--- Current Row Counts ---")
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"{table}: {count} rows")
            
except Exception as e:
    print(f"Error: {e}")
