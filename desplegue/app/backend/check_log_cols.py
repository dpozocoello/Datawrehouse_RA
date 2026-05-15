
import sqlalchemy as sa
import pandas as pd

def check_columns():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    query = "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'etl_process_log';"
    df = pd.read_sql(query, engine)
    print(df)

if __name__ == "__main__":
    check_columns()
