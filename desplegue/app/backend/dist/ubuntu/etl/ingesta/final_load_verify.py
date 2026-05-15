import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def final_load_and_verify():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        print("Executing final RGD load (etl_waste_chemical_load.sql)...")
        sql_path = r'/opt/eco-sieaa/etl_waste_chemical_load.sql'
        sql = open(sql_path).read()
        cur.execute(sql)
        conn.commit()
        print("Load executed successfully.")
        
        # Verify counts
        cur.execute("SELECT COUNT(*) FROM dw.fact_waste_generation")
        total = cur.fetchone()[0]
        print(f"TOTAL records in fact_waste_generation: {total}")
        
        # Verify orphans (sk_proyecto = -1)
        cur.execute("SELECT COUNT(*) FROM dw.fact_waste_generation WHERE sk_proyecto = -1")
        orphans = cur.fetchone()[0]
        print(f"Orphan records (sk_proyecto = -1): {orphans}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error in final_load: {e}")

if __name__ == "__main__":
    final_load_and_verify()
