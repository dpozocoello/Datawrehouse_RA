import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def audit_schema():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        dims = ['dim_proyecto', 'dim_geografia', 'dim_area']
        for dim in dims:
            print(f"\n--- Schema audit for dw.{dim} ---")
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_schema='dw' AND table_name='{dim}'
                ORDER BY ordinal_position
            """)
            cols = cur.fetchall()
            for col in cols:
                prefix = "[*]" if col[2] == 'NO' else "[ ]"
                print(f"{prefix} {col[0]} ({col[1]})")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_schema()
