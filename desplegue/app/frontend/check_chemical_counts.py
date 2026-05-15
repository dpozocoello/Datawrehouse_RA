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
        'dw.fact_chemical_movement',
        'stg.stg_fact_chemical_application',
        'stg.stg_chemical_substances_declaration',
        'stg.stg_chemical_substances_movements'
    ]
    
    with engine.connect() as conn:
        print("--- Table Row Counts ---")
        for table in tables:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"{table}: {count} rows")
            except Exception as e:
                print(f"Error checking {table}: {e}")
            
except Exception as e:
    print(f"General Error: {e}")
