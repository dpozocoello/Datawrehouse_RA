import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY

def deep_audit():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        target_id = 542234
        print(f"Deep Audit for Project {target_id}")
        
        # 1. Main Certificate Table
        print("\n--- coa_mae.certificate_intersection_coa ---")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='coa_mae' AND table_name='certificate_intersection_coa'")
        cols = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT * FROM coa_mae.certificate_intersection_coa WHERE prco_id = %s", (target_id,))
        row = cur.fetchone()
        if row:
            data = {cols[i]: row[i] for i in range(len(row))}
            for k, v in data.items():
                print(f"{k}: {str(v)}")
        
        # 2. Details Table
        print("\n--- coa_mae.details_intersection_project_licencing ---")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='coa_mae' AND table_name='details_intersection_project_licencing'")
        cols = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT * FROM coa_mae.details_intersection_project_licencing WHERE prco_id = %s", (target_id,))
        rows = cur.fetchall()
        for row in rows:
            data = {cols[i]: row[i] for i in range(len(row))}
            for k, v in data.items():
                print(f"{k}: {str(v)}")
            print("-" * 20)
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    deep_audit()
