import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_SUIA_ENLISY

def check_suia_iii():
    try:
        conn = psycopg2.connect(
            host=CONN_SUIA_ENLISY['host'],
            port=CONN_SUIA_ENLISY['port'],
            database=CONN_SUIA_ENLISY['database'],
            user=CONN_SUIA_ENLISY['user'],
            password=CONN_SUIA_ENLISY['password']
        )
        cur = conn.cursor()
        print("### TABLES in suia_iii on 179 ###")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'suia_iii' AND table_name LIKE '%waste%'")
        for t in cur.fetchall():
            print(t[0])
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_suia_iii()
