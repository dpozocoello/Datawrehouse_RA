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

def debug_query():
    # Usar execute directo para ver el error real sin wraps de pandas
    query = text("SELECT * FROM coa_mae.layers_coa LIMIT 5")
    try:
        with engine.connect() as conn:
            print("--- Conectado. Ejecutando query... ---")
            result = conn.execute(query)
            rows = result.fetchall()
            print(f"Filas obtenidas: {len(rows)}")
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_query()
