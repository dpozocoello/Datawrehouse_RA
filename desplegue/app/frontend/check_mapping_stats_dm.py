from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Mapping Statistics for Declarations & Movements ---")
        query = text("""
            SELECT 
                'Declarations' as type,
                COUNT(*) as total,
                COUNT(scr.prco_id) as with_prco_id
            FROM stg.stg_chemical_substances_declaration d
            LEFT JOIN stg.stg_chemical_sustances_records scr ON d.chsr_id = scr.chsr_id
            UNION ALL
            SELECT 
                'Movements' as type,
                COUNT(*) as total,
                COUNT(scr.prco_id) as with_prco_id
            FROM stg.stg_chemical_substances_movements m
            LEFT JOIN stg.stg_chemical_sustances_records scr ON m.chsr_id = scr.chsr_id
        """)
        df = pd.read_sql(query, conn)
        print(df.to_string())
            
except Exception as e:
    print(f"Error: {e}")
