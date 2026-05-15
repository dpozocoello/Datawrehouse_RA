from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def list_tables():
    q = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'dw' AND table_type = 'BASE TABLE'"
    df = pd.read_sql(q, engine)
    print(df.to_string())

if __name__ == "__main__":
    list_tables()
