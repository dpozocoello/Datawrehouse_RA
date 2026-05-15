import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_SUIA_ENLISY

def check_extra():
    try:
        conn = psycopg2.connect(
            host=CONN_SUIA_ENLISY['host'],
            port=CONN_SUIA_ENLISY['port'],
            database=CONN_SUIA_ENLISY['database'],
            user=CONN_SUIA_ENLISY['user'],
            password=CONN_SUIA_ENLISY['password']
        )
        cur = conn.cursor()
        
        # 1. Tablas en coa_waste_generator_record
        print("### TABLES IN coa_waste_generator_record ###")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'coa_waste_generator_record'")
        for t in cur.fetchall():
            print(t[0])
            
        # 2. Verificar conteo de 'other_pronouncement'
        try:
            cur.execute("SELECT count(*) FROM coa_waste_generator_record.waste_generator_record_other_pronouncement")
            print(f"\nTotal in other_pronouncement: {cur.fetchone()[0]}")
        except:
            print("\nTable other_pronouncement not found or error.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_extra()
