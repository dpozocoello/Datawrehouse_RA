from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        'stg.stg_chemical_substance',
        'stg.stg_chemical_sustances_records',
        'stg.stg_chemical_substances_declaration',
        'stg.stg_chemical_substances_movements'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            print(f"--- Sample from {table} ---")
            try:
                df = pd.read_sql(text(f"SELECT * FROM {table} LIMIT 5"), conn)
                print(df.to_string())
            except Exception as e:
                print(f"Error reading {table}: {e}")
            print("\n")
            
except Exception as e:
    print(f"General Error: {e}")
