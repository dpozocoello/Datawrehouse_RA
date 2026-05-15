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

def list_coa_mae():
    query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'coa_mae'")
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            df.to_csv('d:/Datawrehouse_RA/coa_mae_tables.csv', index=False)
            print(f"Encontradas {len(df)} tablas en coa_mae.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_coa_mae()
