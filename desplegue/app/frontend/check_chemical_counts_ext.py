from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        'stg.stg_chemical_substance',
        'stg.stg_chemical_storage',
        'stg.stg_chemical_sustances_records',
        'dw.dim_chemical_importer'
    ]
    
    with engine.connect() as conn:
        print("--- Table Row Counts (Extended) ---")
        for table in tables:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"{table}: {count} rows")
            except Exception as e:
                print(f"Error checking {table}: {e}")
            
except Exception as e:
    print(f"General Error: {e}")
