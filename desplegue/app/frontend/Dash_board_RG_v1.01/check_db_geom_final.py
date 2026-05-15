import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

try:
    print("Checking columns of 'dw.dim_geografia'...")
    df = pd.read_sql("SELECT * FROM dw.dim_geografia LIMIT 1", engine)
    print(f"Columns: {df.columns.tolist()}")
    
    print("\nChecking for any table with 'geom' in its columns...")
    query = """
    SELECT table_schema, table_name, column_name, data_type
    FROM information_schema.columns
    WHERE (column_name LIKE '%%geom%%' OR data_type LIKE '%%geometry%%')
      AND table_schema IN ('dw', 'public')
    """
    df_geom = pd.read_sql(query, engine)
    if not df_geom.empty:
        print(df_geom.to_string())
    else:
        print("No geometry columns found in 'dw' or 'public'.")
except Exception as e:
    print(f"Error: {e}")
