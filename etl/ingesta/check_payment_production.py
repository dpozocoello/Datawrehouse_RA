import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_SUIA_ENLISY

def check_payments():
    try:
        # 1. Audit schemas in the current DB
        conn = psycopg2.connect(
            host=CONN_SUIA_ENLISY['host'],
            port=CONN_SUIA_ENLISY['port'],
            database=CONN_SUIA_ENLISY['database'],
            user=CONN_SUIA_ENLISY['user'],
            password=CONN_SUIA_ENLISY['password']
        )
        cur = conn.cursor()
        print("### SCHEMAS on 179 (suia_enlisy) ###")
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE '%bpms%'")
        for s in cur.fetchall():
            print(s[0])
            
        # 2. Check for payment related tables in public or other schemas
        print("\n### PAYMENT RELATED TABLES on 179 ###")
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%payment%' OR table_name LIKE '%pago%'")
        for t in cur.fetchall():
            print(f"{t[0]}.{t[1]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_payments()
