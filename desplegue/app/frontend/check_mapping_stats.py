from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Mapping Statistics for Imports ---")
        query = text("""
            SELECT 
                COUNT(*) as total_imports,
                COUNT(scr.prco_id) as imports_with_prco_id
            FROM stg.stg_import_request ir
            LEFT JOIN stg.stg_chemical_sustances_records scr ON ir.chsr_id = scr.chsr_id
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
