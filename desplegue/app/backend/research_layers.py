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

def explore_layers():
    print("--- Explorando capas en coa_mae.layers ---")
    try:
        # Intentar encontrar la tabla de capas
        query = """
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name ILIKE '%layer%' OR table_name ILIKE '%capa%'
        """
        tables = pd.read_sql(query, engine)
        print("Tablas encontradas:", tables)
        
        # Si existe coa_mae.layers_coa o algo similar
        query_layers = "SELECT * FROM coa_mae.layers_coa" # Basado en el nombre layer_id en ingesta_intersection.py
        layers = pd.read_sql(query_layers, engine)
        print("\nCapas encontradas en coa_mae.layers_coa:")
        print(layers[['laye_id', 'laye_name']])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_layers()
