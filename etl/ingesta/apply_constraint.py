import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL

def apply_constraint():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        print("Applying UNIQUE constraint (sk_proyecto, certificate_code)...")
        cur.execute("ALTER TABLE dw.dim_intersection ADD CONSTRAINT unique_proj_cert UNIQUE (sk_proyecto, certificate_code);")
        conn.commit()
        print("Constraint applied successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR/WARNING: {e}")

if __name__ == "__main__":
    apply_constraint()
