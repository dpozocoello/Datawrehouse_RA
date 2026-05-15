
import psycopg2
from ETL_p.config import CONN_SUIA_ENLISY

def inspect_columns():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'geographical_locations' AND table_schema = 'public'")
        cols = cur.fetchall()
        for c in cols:
            print(f"COL: {c[0]} ({c[1]})")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_columns()
