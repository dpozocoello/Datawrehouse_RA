from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8')

def test_project_registry():
    query = '''
    SELECT 
        p.nombre_proyecto as "Nombre del Proyecto",
        p.codigo_proyecto as "Código Proyecto",
        g.codigo as "Código Registro Gestor",
        g.ruc_generator as "RUC",
        g.generator_name as "Razón Social",
        g.province as "Provincia",
        g.canton as "Cantón",
        SUM(f.quantity_generated) as "Total (kg)"
    FROM dw.fact_waste_generation f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_waste_generator g ON f.waste_generator_key = g.waste_generator_key
    GROUP BY p.nombre_proyecto, p.codigo_proyecto, g.codigo, g.ruc_generator, g.generator_name, g.province, g.canton
    ORDER BY "Total (kg)" DESC
    LIMIT 5
    '''
    try:
        df = pd.read_sql(query, engine)
        print("--- Test Project Registry ---")
        print(df)
    except Exception as e:
        print(f"Error: {e}")

test_project_registry()
