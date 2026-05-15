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
        conn.set_client_encoding('LATIN1') # Try LATIN1
        cur = conn.cursor()
        cur.execute("SELECT nspname FROM pg_namespace")
        schemas = [row[0] for row in cur.fetchall()]
        with open('F:/Datawrehouse_RA/schemas_list.txt', 'w', encoding='utf-8') as f:
            for s in schemas:
                f.write(repr(s) + "\n")
        cur.close()
        conn.close()
    except Exception as e:
        with open('F:/Datawrehouse_RA/schemas_list.txt', 'w', encoding='utf-8') as f:
            f.write("ERROR: " + str(e))

if __name__ == "__main__":
    list_schemas()
