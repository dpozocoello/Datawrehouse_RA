import pandas as pd
import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

def check_one_table():
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        print("--- Leyendo coa_mae.certificate_intersection_coa ---")
        df = pd.read_sql_query("SELECT * FROM coa_mae.certificate_intersection_coa LIMIT 5", conn)
        print(df)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_one_table()
