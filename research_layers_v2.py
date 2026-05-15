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

def explore_layers():
    print("--- Explorando capas (V1.8.4) ---")
    query = text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name ILIKE '%layer%'")
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            print(df)
            
            # Probar si existe coa_mae.layers_coa
            print("--- Intentando leer coa_mae.layers_coa ---")
            df_lc = pd.read_sql(text("SELECT * FROM coa_mae.layers_coa LIMIT 5"), conn)
            print(df_lc)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_layers()
