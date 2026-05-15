from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Linking stg.stg_chemical_sustances_records to dw.dim_proyecto ---")
        query = text("""
            SELECT 
                s.chsr_id,
                s.prco_id,
                dp.sk_proyecto,
                dp.codigo_proyecto
            FROM stg.stg_chemical_sustances_records s
            JOIN dw.dim_proyecto dp ON dp.codigo_proyecto LIKE '%' || s.prco_id::text
            LIMIT 10
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
