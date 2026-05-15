import psycopg2

def find_function_in_dw():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dw_reg_v1",
            user="postgres",
            password="postgres",
            port=5432
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT n.nspname, p.proname 
            FROM pg_proc p 
            JOIN pg_namespace n ON p.pronamespace = n.oid 
            WHERE p.proname ILIKE '%sp_coa_bi%';
        """)
        rows = cur.fetchall()
        with open('F:/Datawrehouse_RA/func_find.txt', 'w') as f:
            for row in rows:
                f.write(f"Schema: {row[0]} | Func: {row[1]}\n")
        cur.close()
        conn.close()
    except Exception as e:
        with open('F:/Datawrehouse_RA/func_find.txt', 'w') as f:
            f.write(repr(e))

if __name__ == "__main__":
    find_function_in_dw()
