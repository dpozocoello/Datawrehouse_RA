from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8')

def diagnose_na_v2():
    query = '''
    SELECT 
        geo.provincia as geo_prov,
        gen.province as gen_prov,
        f.source_system,
        COUNT(*) as record_count,
        SUM(f.quantity_generated) as total_qty
    FROM dw.fact_waste_generation f
    LEFT JOIN dw.dim_geografia geo ON f.geo_location_key = geo.sk_geografia
    LEFT JOIN dw.dim_waste_generator gen ON f.waste_generator_key = gen.waste_generator_key
    WHERE (geo.provincia = 'N/A' OR geo.provincia IS NULL) AND f.quantity_generated > 0
    GROUP BY geo.provincia, gen.province, f.source_system
    ORDER BY total_qty DESC
    LIMIT 20
    '''
    try:
        df = pd.read_sql(query, engine)
        print("--- Diagnosis V2 of N/A Province ---")
        pd.set_option('display.max_columns', None); pd.set_option('display.width', 1000)
        print(df)
    except Exception as e:
        print(f"Error: {e}")

diagnose_na_v2()
