import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

def run_query(q):
    try:
        return pd.read_sql(q, engine)
    except Exception as e:
        return str(e)

print("--- Tablas en dw ---")
tables = run_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'dw'")
print(tables)

print("\n--- Columnas en dw.fact_regularizacion ---")
cols = run_query("SELECT * FROM dw.fact_regularizacion LIMIT 0")
if isinstance(cols, pd.DataFrame):
    print(cols.columns.tolist())
else:
    print(cols)

print("\n--- Buscando capas específicas en areas_protegidas o similar ---")
# El usuario menciona: SNAP, ZONAS INTANGIBLES, BOSQUES PROTECTORES, PATRIMONIO FORESTAL DEL ESTADO
# Vamos a buscar estas palabras en todas las columnas de texto de fact_regularizacion
search_terms = ['SNAP', 'INTANGIBLE', 'BOSQUE', 'PATRIMONIO', 'FORESTAL']
text_cols = ['areas_protegidas', 'interseccion_snap'] # Basado en mi anterior descubrimiento

for term in search_terms:
    print(f"\nBuscando '{term}':")
    for col in text_cols:
        res = run_query(f"SELECT {col}, COUNT(*) FROM dw.fact_regularizacion WHERE {col} ILIKE '%%{term}%%' GROUP BY 1")
        if isinstance(res, pd.DataFrame) and not res.empty:
            print(f"Encontrado en {col}:")
            print(res)

# Verificar si hay una tabla dw.dim_area o similar que contenga estas capas
print("\n--- Inspeccionando dw.dim_area si existe ---")
if isinstance(tables, pd.DataFrame) and 'dim_area' in tables['table_name'].values:
    print(run_query("SELECT * FROM dw.dim_area LIMIT 10"))
    print("\nTipos de área en dim_area:")
    print(run_query("SELECT DISTINCT tipo_area FROM dw.dim_area")) # Asumiendo tipo_area es la columna
else:
    # Ver columnas de todas las tablas dw.*_area por si acaso
    area_tables = [t for t in tables['table_name'].values if 'area' in t]
    for at in area_tables:
        print(f"\nColumnas en dw.{at}:")
        print(run_query(f"SELECT * FROM dw.{at} LIMIT 0").columns.tolist())

# Buscar la sección "Validador y Verificación de Proyectos" en el código
print("\n--- Buscando tabs en el código ---")
# Esto se hará con grep_search después
