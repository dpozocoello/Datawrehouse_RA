import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY

def check_cols():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        cur.execute("SELECT * FROM coa_mae.certificate_intersection_coa LIMIT 0")
        with open('prod_cols.log', 'w') as f:
            for desc in cur.description:
                f.write(f"{desc[0]}/n")
        print("Columns written to prod_cols.log")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_cols()
