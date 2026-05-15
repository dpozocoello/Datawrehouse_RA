import pandas as pd
import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179", "port": 5632, "database": "suia_enlisy", "user": "postgres", "password": "postgres"
}

def list_suia_iii_layers():
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        df = pd.read_sql_query("SELECT laye_id, laye_name FROM suia_iii.layers", conn)
        # Buscar coincidencias
        patterns = ['SNAP', 'INTANGIBLE', 'BOSQUE', 'PATRIMONIO']
        for p in patterns:
            print(f"--- Patrón: {p} ---")
            print(df[df['laye_name'].str.contains(p, case=False, na=False)].to_string())
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_suia_iii_layers()
