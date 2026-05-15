import pandas as pd
from sqlalchemy import create_engine

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres",
}

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine = create_engine(build_uri(CONN_DWH_LOCAL))

def get_columns():
    for table in ['dim_intersection', 'dim_proyecto']:
        print(f"--- Columns for {table} ---")
        query = f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'dw' 
            AND table_name = '{table}'
            ORDER BY ordinal_position
        """
        df = pd.read_sql(query, engine)
        print(df.to_string())

if __name__ == "__main__":
    get_columns()
