import psycopg2

def list_schemas():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Datawarehouse_RA",
            user="postgres",
            password="postgres",
            port=5432
        )
        cur = conn.cursor()
        cur.execute("SELECT nspname FROM pg_catalog.pg_namespace WHERE nspname NOT LIKE 'pg_%%' AND nspname != 'information_schema'")
        schemas = [r[0] for r in cur.fetchall()]
        print(f"Schemas: {schemas}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_schemas()
