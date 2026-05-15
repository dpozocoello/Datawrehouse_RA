import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

print("--- Columnas en dw.fact_regularizacion ---")
df_cols = pd.read_sql("SELECT * FROM dw.fact_regularizacion LIMIT 0", engine)
cols = df_cols.columns.tolist()
print(cols)

# Intentar buscar tablas en el esquema dw que puedan tener la información de intersección
print("\n--- Tablas en el esquema dw ---")
df_tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'dw'", engine)
print(df_tables)

# Buscar en fact_regularizacion columnas que puedan contener el nombre de la capa o intersección
relevant_cols = [c for c in cols if any(word in c.lower() for word in ['interseccion', 'area', 'superposicion', 'snap'])]
print(f"\n--- Columnas potencialmente relevantes en fact_regularizacion: {relevant_cols} ---")

if relevant_cols:
    for col in relevant_cols:
        print(f"\nValores únicos en {col}:")
        try:
            print(pd.read_sql(f"SELECT {col}, COUNT(*) FROM dw.fact_regularizacion GROUP BY 1 ORDER BY 2 DESC LIMIT 10", engine))
        except Exception as e:
            print(f"Error consultando {col}: {e}")

# Revisar si existe dw.dim_area
if 'dim_area' in df_tables['table_name'].values:
    print("\n--- Inspeccionando dw.dim_area ---")
    df_area_cols = pd.read_sql("SELECT * FROM dw.dim_area LIMIT 0", engine)
    print(f"Columnas en dim_area: {df_area_cols.columns.tolist()}")
    # Ver algunos valores si la columna existe (asumiendo nombres comunes)
    try:
        df_area_sample = pd.read_sql("SELECT * FROM dw.dim_area LIMIT 10", engine)
        print(df_area_sample)
    except Exception as e:
        print(f"Error: {e}")
else:
    print("\nNo se encontró dw.dim_area")

# Buscar proyectos que intersecten con las capas que el usuario mencionó
print("\n--- Buscando menciones de capas en areas_protegidas o similar ---")
query_search = """
SELECT areas_protegidas, COUNT(*) 
FROM dw.fact_regularizacion 
WHERE areas_protegidas IS NOT NULL 
GROUP BY 1 
ORDER BY 2 DESC 
LIMIT 20
"""
try:
    print(pd.read_sql(query_search, engine))
except Exception as e:
    print(e)
