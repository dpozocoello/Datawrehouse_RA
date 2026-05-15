
import psycopg2

def check_levels():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        cur.execute("SELECT level, count(*) FROM stg.geographical_locations_bi GROUP BY level ORDER BY level")
        print(cur.fetchall())
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_levels()
