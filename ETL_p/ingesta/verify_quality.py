import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL

def verify_quality():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        
        # 1. COA Quality
        cur.execute("""
            SELECT count(*), count(dangerous_waste_key), count(danger_class_key) 
            FROM dw.fact_waste_generation f 
            JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto 
            WHERE p.codigo_proyecto LIKE 'MAE-RA-2016-%'
        """)
        coa_res = cur.fetchone()
        
        # 2. RCOA Quality
        cur.execute("""
            SELECT count(*), count(dangerous_waste_key), count(danger_class_key) 
            FROM dw.fact_waste_generation f 
            JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto 
            WHERE p.codigo_proyecto NOT LIKE 'MAE-RA-2016-%'
        """)
        rcoa_res = cur.fetchone()
        
        print("====================================================")
        print("UNIFIED RGD QUALITY AUDIT (v1.6.8)")
        print("====================================================")
        print(f"COA Path (124k expected): Total={coa_res[0]}, DangerousWaste={coa_res[1]}, DangerClass={coa_res[2]}")
        print(f"RCOA Path (208k expected): Total={rcoa_res[0]}, DangerousWaste={rcoa_res[1]}, DangerClass={rcoa_res[2]}")
        print("====================================================")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_quality()
