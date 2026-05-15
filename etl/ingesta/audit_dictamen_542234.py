import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY

def audit_dictamen():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        target_id = 542234
        print(f"Auditing Project: {target_id} in coa_mae.certificate_intersection_coa")
        
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'coa_mae' AND table_name = 'certificate_intersection_coa'
        """)
        cols = [r[0] for r in cur.fetchall()]
        print(f"Columns: {cols}")
        
        cur.execute("SELECT * FROM coa_mae.certificate_intersection_coa WHERE prco_id = %s LIMIT 1", (target_id,))
        row = cur.fetchone()
        if row:
            for i, val in enumerate(row):
                print(f"{cols[i]}: {str(val)[:100]}...")
        else:
            print("Project not found in production.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_dictamen()
