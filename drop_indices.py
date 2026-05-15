import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))
from config import CONN_DWH_LOCAL
from connections import get_connection

def drop_indices():
    with get_connection(CONN_DWH_LOCAL, autocommit=True) as conn:
        with conn.cursor() as cur:
            print("Dropping indices...")
            cur.execute("DROP INDEX IF EXISTS dw.idx_fact_snap;")
            cur.execute("DROP INDEX IF EXISTS dw.idx_fact_areas;")
            print("Indices dropped.")

if __name__ == "__main__":
    drop_indices()
