import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def inspect():
    tables = ['dim_area', 'dim_geografia', 'v_dashboard_regularizacion']
    for table in tables:
        print(f"\n--- COLUMN NAMES: {table} ---")
        df_cols = pd.read_sql(f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = '{table}'", engine)
        print(df_cols['column_name'].tolist())

        print(f"\n--- SAMPLE DATA (5 rows): {table} ---")
        df_sample = pd.read_sql(f"SELECT * FROM dw.{table} LIMIT 5", engine)
        print(df_sample.to_string())

if __name__ == "__main__":
    inspect()
