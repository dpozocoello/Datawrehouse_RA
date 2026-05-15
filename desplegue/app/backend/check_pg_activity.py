import psycopg2
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_DWH_LOCAL

def check_activity():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password'],
            database=CONN_DWH_LOCAL['database'],
            connect_timeout=5
        )
        cur = conn.cursor()
        cur.execute("SELECT pid, datname, state, query, wait_event_type, wait_event FROM pg_stat_activity")
        rows = cur.fetchall()
        for r in rows:
            print(r)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_activity()
