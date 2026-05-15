
import sqlalchemy as sa
import pandas as pd

def check_all_cols():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    tables = [
        "stg.stg_import_request",
        "stg.stg_chemical_sustances_records",
        "stg.stg_chemical_substances_declaration"
    ]
    for table in tables:
        schema, name = table.split('.')
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{name}';"
        df = pd.read_sql(query, engine)
        print(f"\nColumns for {table}:")
        print(df['column_name'].tolist())

if __name__ == "__main__":
    check_all_cols()
