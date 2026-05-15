import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def bulletproof_audit():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        dims = [
            ('dim_proyecto', 'sk_proyecto'),
            ('dim_geografia', 'sk_geografia'),
            ('dim_area', 'sk_area'),
            ('dim_tiempo', 'sk_tiempo'),
            ('dim_waste_type', 'waste_type_key'),
            ('dim_waste_generator', 'waste_generator_key')
        ]
        
        for table, col in dims:
            try:
                # First check if the SK column exists in this table (some use different names)
                cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='dw' AND table_name='{table}' AND column_name='{col}'")
                if not cur.fetchone():
                    # Try to find the leading sk_ column
                    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='dw' AND table_name='{table}' AND column_name LIKE 'sk_%%' LIMIT 1")
                    res = cur.fetchone()
                    if res: col = res[0]
                    else: continue

                cur.execute(f"SELECT COUNT(*) FROM dw.{table} WHERE {col} = -1")
                count = cur.fetchone()[0]
                print(f"[{table}] has -1 record: {'YES' if count > 0 else 'NO'}")
            except Exception as e:
                print(f"Error checking {table}: {e}")
                conn.rollback()
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    bulletproof_audit()
