import pandas as pd
from sqlalchemy import create_engine

CONN_SUIA_ENLISY = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine = create_engine(build_uri(CONN_SUIA_ENLISY))

def check_tables():
    tables_to_check = [
        'coa_mae.intersections_project_licencing_coa',
        'coa_mae.project_licencing_coa',
        'coa_mae.layers_coa'
    ]
    for table in tables_to_check:
        try:
            print(f"--- Checking {table} ---")
            query = f"SELECT * FROM {table} LIMIT 1"
            pd.read_sql(query, engine)
            print(f"[OK] {table} exists.")
        except Exception as e:
            print(f"[ERROR] {table}: {e}")

if __name__ == "__main__":
    check_tables()
