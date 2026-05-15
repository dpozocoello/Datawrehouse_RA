import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY

def final_table_check():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        # 1. List ALL coa_mae tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'coa_mae' AND table_name LIKE '%%intersection%%'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"Intersection Tables: {tables}")
        
        target_id = 542234
        for table in tables:
            print(f"\nChecking table: {table}")
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='coa_mae' AND table_name='{table}'")
            cols = [r[0] for r in cur.fetchall()]
            
            if 'prco_id' in cols:
                cur.execute(f"SELECT * FROM coa_mae.{table} WHERE prco_id = {target_id}")
                row = cur.fetchone()
                if row:
                    data = {cols[i]: row[i] for i in range(len(row))}
                    for k, v in data.items():
                        print(f"  {k}: {str(v)}")
            elif 'cein_id' in cols:
                cur.execute(f"SELECT cein_id FROM coa_mae.certificate_intersection_coa WHERE prco_id = {target_id}")
                cein_ids = [r[0] for r in cur.fetchall()]
                if cein_ids:
                    cur.execute(f"SELECT * FROM coa_mae.{table} WHERE cein_id IN ({','.join(map(str, cein_ids))})")
                    rows = cur.fetchall()
                    for row in rows:
                        data = {cols[i]: row[i] for i in range(len(row))}
                        print(f"  DATA ({table}): {data}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_table_check()
