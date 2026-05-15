import pandas as pd
from sqlalchemy import create_engine, text

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

def check_intersections_project():
    try:
        print("--- Columns for coa_mae.intersections_project ---")
        query = text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'coa_mae' AND table_name = 'intersections_project'")
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            print(df)
            
        print("\n--- Rows for coa_mae.intersections_project (LIMIT 5) ---")
        query_rows = text("SELECT * FROM coa_mae.intersections_project LIMIT 5")
        with engine.connect() as conn:
            df_rows = pd.read_sql(query_rows, conn)
            print(df_rows)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_intersections_project()
