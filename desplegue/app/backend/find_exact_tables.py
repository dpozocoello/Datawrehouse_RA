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

def find_exact_tables():
    patterns = ['intersections_project_licencing_coa', 'project_licencing_coa', 'layers_coa']
    for p in patterns:
        query = text(f"SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = '{p}'")
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                print(df)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    find_exact_tables()
