import psycopg2
import sys
import os

sys.path.insert(0, r'/opt/eco-sieaa/etl')
from config import CONN_DWH_LOCAL

def check_schema():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        query = "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'stg' AND table_name = 'online_payments_historical_bi'"
        cur.execute(query)
        rows = cur.fetchall()
        print("### SCHEMA FOR stg.online_payments_historical_bi ###")
        for row in rows:
            print(row)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_schema()
