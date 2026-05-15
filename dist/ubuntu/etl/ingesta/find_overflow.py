import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def find_overflow():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        print("Searching for numeric overflow cases in stg.stg_fact_waste_generation...")
        # 10^12 is the limit for NUMERIC(15,3)
        limit = 10**12
        cur.execute(f"""
            SELECT project_code, quantity_generated, quantity_delivered, quantity_stored 
            FROM stg.stg_fact_waste_generation 
            WHERE quantity_generated >= {limit} 
               OR quantity_delivered >= {limit} 
               OR quantity_stored >= {limit}
        """)
        rows = cur.fetchall()
        if rows:
            print(f"FOUND {len(rows)} problematic records:")
            for r in rows:
                print(f"Proj: {r[0]} | Gen: {r[1]} | Del: {r[2]} | Sto: {r[3]}")
        else:
            print("No records found with values >= 10^12.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_overflow()
