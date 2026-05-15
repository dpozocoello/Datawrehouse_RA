import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL

def final_validate():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        
        # 1. RGD
        cur.execute("SELECT count(*) FROM dw.fact_waste_generation")
        rgd_total = cur.fetchone()[0]
        print(f"RGD Total Records (dw.fact_waste_generation): {rgd_total}")
        
        # 2. Intersection
        cur.execute("SELECT count(*) FROM dw.dim_intersection")
        int_total = cur.fetchone()[0]
        print(f"SNAP Certificates Total (dw.dim_intersection): {int_total}")
        
        # 3. Audit specific project 495449
        cur.execute("""
            SELECT di.certificate_code, LEFT(di.html_location, 100) 
            FROM dw.dim_intersection di
            JOIN dw.dim_proyecto dp ON di.sk_proyecto = dp.sk_proyecto
            WHERE dp.sk_proyecto = (SELECT sk_proyecto FROM dw.dim_proyecto WHERE sk_proyecto = 1000 -- Just a guess ID for testing linking
                                   OR codigo_proyecto = 'MAATE-RA-2023-446726' LIMIT 1)
        """)
        audit = cur.fetchall()
        print(f"Audit Intersection Link: {audit}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    final_validate()
