import psycopg2

SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}

def list_tables():
    try:
        conn = psycopg2.connect(**SUIA_PARAMS)
        cur = conn.cursor()
        print("--- Tablas en coa_mae ---")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'coa_mae'")
        tables = [row[0] for row in cur.fetchall()]
        print(tables)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
