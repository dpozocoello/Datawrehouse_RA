import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL

def check_cols():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        print("Columns in dw.dim_proyecto:")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'dim_proyecto'")
        for c in cur.fetchall():
            print(f"  {c[0]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_cols()
