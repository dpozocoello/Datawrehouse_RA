import psycopg2

SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}

def find_layer_table():
    try:
        conn = psycopg2.connect(**SUIA_PARAMS)
        cur = conn.cursor()
        print("--- Buscando tablas tipo 'layer' ---")
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%layer%'")
        rows = cur.fetchall()
        for row in rows:
            print(row)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_layer_table()
