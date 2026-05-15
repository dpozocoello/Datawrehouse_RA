import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def search_patterns():
    ids = ['383502', '67988']
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        for pid in ids:
            print(f"Searching for {pid}...")
            cur.execute(f"SELECT codigo_proyecto FROM dw.dim_proyecto WHERE codigo_proyecto LIKE '%{pid}%'")
            matches = cur.fetchall()
            print(f"  Matches: {matches}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    search_patterns()
