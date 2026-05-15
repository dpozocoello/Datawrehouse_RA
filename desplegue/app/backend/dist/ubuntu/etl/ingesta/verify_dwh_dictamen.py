import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def verify_dwh():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        target_code = 'MAE-RA-2026-588808' # Project 542234 code from image
        print(f"Verifying Project {target_code} in DWH...")
        
        cur.execute("""
            SELECT di.certificate_code, di.dictamen_final 
            FROM dw.dim_intersection di
            JOIN dw.dim_proyecto dp ON di.sk_proyecto = dp.sk_proyecto
            WHERE dp.codigo_proyecto = %s
        """, (target_code,))
        
        row = cur.fetchone()
        if row:
            print(f"Certificate: {row[0]}")
            print(f"Dictamen Final: {row[1]}")
        else:
            print("Project/Intersection not found in DWH.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_dwh()
