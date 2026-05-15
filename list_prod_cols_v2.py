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

def list_columns():
    tables = ['intersections_project_licencing_coa', 'project_licencing_coa', 'layers_coa']
    for table in tables:
        print(f"--- Columns for {table} ---")
        query = text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table}' AND table_schema = 'coa_mae'
        """)
        try:
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                print(df.to_string())
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    list_columns()
