import psycopg2

def list_databases():
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port=5432
        )
        # Use autocommit to list databases
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        dbs = [row[0] for row in cur.fetchall()]
        with open('F:/Datawrehouse_RA/dbs_list.txt', 'w', encoding='utf-8') as f:
            for db in dbs:
                f.write(db + "\n")
        cur.close()
        conn.close()
    except Exception as e:
        with open('F:/Datawrehouse_RA/dbs_list.txt', 'w', encoding='utf-8') as f:
            f.write(repr(e))

if __name__ == "__main__":
    list_databases()
