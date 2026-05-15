import pandas as pd
import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

def check_suia_iii_layers():
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        print("--- Leyendo suia_iii.layers ---")
        df = pd.read_sql_query("SELECT * FROM suia_iii.layers LIMIT 5", conn)
        print(df)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_suia_iii_layers()
