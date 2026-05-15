import psycopg2

def check_remote_schemas():
    try:
        conn = psycopg2.connect(
            host="172.16.0.179",
            database="suia_enlisy",
            user="postgres",
            password="postgres",
            port=5632
        )
        cur = conn.cursor()
        cur.execute("SELECT nspname FROM pg_namespace")
        schemas = [row[0] for row in cur.fetchall()]
        with open('F:/Datawrehouse_RA/remote_schemas.txt', 'w') as f:
            for s in schemas:
                f.write(s + "\n")
        cur.close()
        conn.close()
    except Exception as e:
        with open('F:/Datawrehouse_RA/remote_schemas.txt', 'w') as f:
            f.write(repr(e))

if __name__ == "__main__":
    check_remote_schemas()
