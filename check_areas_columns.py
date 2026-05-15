
import psycopg2

def check_areas_columns():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'stg' AND table_name = 'suia_areas_bi'")
        print(cur.fetchall())
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_areas_columns()
