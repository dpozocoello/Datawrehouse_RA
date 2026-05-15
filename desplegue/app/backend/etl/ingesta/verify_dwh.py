import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL

def verify():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        
        # 1. Total records
        cur.execute("SELECT count(*) FROM dw.fact_waste_generation")
        total = cur.fetchone()[0]
        
        # 2. Historical COA records (using MAE-RA-2016- prefix or similar)
        cur.execute("SELECT count(*) FROM dw.fact_waste_generation f JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto WHERE p.codigo_proyecto LIKE 'MAE-RA-2016-%'")
        coa_count = cur.fetchone()[0]
        
        # 3. Geo completeness
        cur.execute("SELECT count(*) FROM dw.fact_waste_generation WHERE geo_location_key IS NOT NULL")
        geo_count = cur.fetchone()[0]
        
        print("====================================================")
        print("UNIFIED RGD VERIFICATION (v1.6.8)")
        print("====================================================")
        print(f"Total Records in DWH: {total}")
        print(f"Historical COA Records: {coa_count}")
        print(f"Records with Geography: {geo_count} ({(geo_count/total)*100:.1f}%)")
        print("====================================================")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify()
