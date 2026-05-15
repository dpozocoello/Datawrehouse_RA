import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def check_uniqueness():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        print("Checking uniqueness of project ID suffixes...")
        cur.execute("""
            SELECT internal_id, COUNT(*) 
            FROM (
                SELECT split_part(codigo_proyecto, '-', array_length(string_to_array(codigo_proyecto, '-'), 1)) as internal_id 
                FROM dw.dim_proyecto
                WHERE codigo_proyecto IS NOT NULL AND codigo_proyecto != ''
            ) sub 
            GROUP BY internal_id 
            HAVING COUNT(*) > 1 
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """)
        dupes = cur.fetchall()
        print(f"Top non-unique internal IDs: {dupes}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    check_uniqueness()
