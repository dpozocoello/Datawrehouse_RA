import pandas as pd
import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

def find_layers_fixed():
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        query = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_name ILIKE '%layer%'"
        df = pd.read_sql_query(query, conn)
        print(df)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_layers_fixed()
