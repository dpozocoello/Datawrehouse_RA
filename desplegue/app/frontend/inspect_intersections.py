import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

print("--- Columnas en dw.fact_regularizacion ---")
df_cols = pd.read_sql("SELECT * FROM dw.fact_regularizacion LIMIT 0", engine)
print(df_cols.columns.tolist())

# Intentar buscar tablas en el esquema dw que puedan tener la información de intersección
print("\n--- Tablas en el esquema dw ---")
df_tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'dw'", engine)
print(df_tables)

print("\n--- Valores únicos en interseccion_snap (sk_proyecto vs fact) ---")
# Ver si hay una columna en dim_proyecto o fact_regularizacion
query = """
SELECT 
    interseccion_snap, 
    COUNT(*) as count 
FROM dw.fact_regularizacion 
GROUP BY 1
"""
try:
    df_snap = pd.read_sql(query, engine)
    print(df_snap)
except Exception as e:
    print(f"Error consultando interseccion_snap: {e}")

# Buscar específicamente las capas mencionadas por el usuario
print("\n--- Buscando capas ambientales en la base de datos ---")
# A veces la información está en dw.dim_area o similar si existe
if 'dim_area' in df_tables['table_name'].values:
    print("Encontrada tabla dw.dim_area, inspeccionando...")
    df_area = pd.read_sql("SELECT * FROM dw.dim_area LIMIT 5", engine)
    print(df_area)
    df_area_types = pd.read_sql("SELECT DISTINCT tipo_area FROM dw.dim_area", engine)
    print("Tipos de área en dim_area:")
    print(df_area_types)
else:
    print("No se encontró dw.dim_area")

# Buscar en fact_regularizacion columnas que puedan contener el nombre de la capa
relevant_cols = [c for c in df_cols.columns.tolist() if any(word in c.lower() for word in ['bosque', 'intangible', 'forestal', 'interseccion', 'area', 'superposicion'])]
print(f"\n--- Columnas potencialmente relevantes en fact_regularizacion: {relevant_cols} ---")

if relevant_cols:
    for col in relevant_cols:
        print(f"\nValores en {col}:")
        print(pd.read_sql(f"SELECT {col}, COUNT(*) FROM dw.fact_regularizacion GROUP BY 1 ORDER BY 2 DESC LIMIT 5", engine))
