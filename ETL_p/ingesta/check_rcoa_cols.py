import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_SUIA_ENLISY

def check_rcoa_cols():
    try:
        conn = psycopg2.connect(
            host=CONN_SUIA_ENLISY['host'],
            port=CONN_SUIA_ENLISY['port'],
            database=CONN_SUIA_ENLISY['database'],
            user=CONN_SUIA_ENLISY['user'],
            password=CONN_SUIA_ENLISY['password']
        )
        cur = conn.cursor()
        
        tables = [
            'waste_waste_generation_points',
            'waste_generator_record_coa'
        ]
        
        for t in tables:
            print(f"\n### COLUMNS IN coa_waste_generator_record.{t} ###")
            cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'coa_waste_generator_record' AND table_name = '{t}'")
            for col in cur.fetchall():
                print(f"  {col[0]} ({col[1]})")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_rcoa_cols()
