
import sqlalchemy as sa
import pandas as pd

def check_cols():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    query = "SELECT column_name FROM information_schema.columns WHERE table_schema = 'stg' AND table_name = 'stg_chemical_substances_movements';"
    df = pd.read_sql(query, engine)
    print(df)

if __name__ == "__main__":
    check_cols()
