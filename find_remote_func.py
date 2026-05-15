import psycopg2

def check_remote_funcs():
    try:
        conn = psycopg2.connect(
            host="172.16.0.179",
            database="suia_enlisy",
            user="postgres",
            password="postgres",
            port=5632
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT n.nspname, p.proname 
            FROM pg_proc p 
            JOIN pg_namespace n ON p.pronamespace = n.oid 
            WHERE p.proname ILIKE '%sp_coa_bi%';
        """)
        rows = cur.fetchall()
        with open('F:/Datawrehouse_RA/remote_func_find.txt', 'w') as f:
            for row in rows:
                f.write(f"Schema: {row[0]} | Func: {row[1]}\n")
        cur.close()
        conn.close()
    except Exception as e:
        with open('F:/Datawrehouse_RA/remote_func_find.txt', 'w') as f:
            f.write(repr(e))

if __name__ == "__main__":
    check_remote_funcs()
