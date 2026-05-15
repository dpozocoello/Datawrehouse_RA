
import psycopg2
from ETL_p.config import CONN_SUIA_ENLISY

def get_columns():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'geographical_locations' AND table_schema = 'public' ORDER BY ordinal_position")
        cols = cur.fetchall()
        with open(r"f:\Datawrehouse_RA\geo_cols.txt", "w") as f:
            for c in cols:
                f.write(f"{c[0]} ({c[1]})\n")
        cur.close()
        conn.close()
    except Exception as e:
        with open(r"f:\Datawrehouse_RA\geo_cols.txt", "w") as f:
            f.write(f"ERROR: {str(e)}")

if __name__ == "__main__":
    get_columns()
