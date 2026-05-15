from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8')

def test_query(name, query):
    print(f"--- Testing {name} ---")
    try:
        df = pd.read_sql(query, engine)
        print(f"Success! Rows: {len(df)}")
        if not df.empty:
            print(df.head(2))
    except Exception as e:
        print(f"Failed: {e}")

query_waste_summary = '''
SELECT 
    geo.provincia, 
    t.waste_name as tipo_desecho, 
    SUM(f.quantity_generated) as total_generado
FROM dw.fact_waste_generation f
JOIN dw.dim_geografia geo ON f.geo_location_key = geo.sk_geografia
JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
GROUP BY geo.provincia, t.waste_name
'''

query_managers = '''
SELECT 
    g.generator_name as "Razón Social",
    g.ruc_generator as "RUC",
    g.province as "Provincia",
    g.canton as "Cantón",
    g.generator_type as "Tipo Perfil",
    SUM(f.quantity_generated) as "Total Generado (kg)"
FROM dw.fact_waste_generation f
JOIN dw.dim_waste_generator g ON f.waste_generator_key = g.waste_generator_key
GROUP BY g.generator_name, g.ruc_generator, g.province, g.canton, g.generator_type
ORDER BY "Total Generado (kg)" DESC
'''

test_query("Waste Summary", query_waste_summary)
test_query("Managers Report", query_managers)
