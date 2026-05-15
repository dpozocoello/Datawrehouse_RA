import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL, CONN_SUIA_ENLISY

def final_validate():
    try:
        # 1. DWH Validation
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM dw.fact_waste_generation")
        total = cur.fetchone()[0]
        print(f"Total Records in DWH (dw.fact_waste_generation): {total}")
        
        cur.execute("SELECT project_code, count(*) FROM stg.stg_fact_waste_generation WHERE project_code = 'SN-PROY' GROUP BY 1")
        orphan_count = cur.fetchone()
        print(f"Orphan Records (SN-PROY) recovered: {orphan_count[1] if orphan_count else 0}")
        
        cur.close()
        conn.close()
        
        # 2. Production Intersection Audit (New Requirement)
        print("\n### AUDIT INTERSECTION SNAP (179) ###")
        conn_prod = psycopg2.connect(
            host=CONN_SUIA_ENLISY['host'],
            port=CONN_SUIA_ENLISY['port'],
            database=CONN_SUIA_ENLISY['database'],
            user=CONN_SUIA_ENLISY['user'],
            password=CONN_SUIA_ENLISY['password']
        )
        cur_p = conn_prod.cursor()
        
        # Audit specific project 495449
        cur_p.execute("SELECT * FROM coa_mae.certificate_intersection_coa WHERE prco_id = 495449")
        rows = cur_p.fetchall()
        cols = [desc[0] for desc in cur_p.description]
        print(f"Project 495449 - Intersection Certificate found: {len(rows)} records")
        for i, row in enumerate(rows):
            print(f"\n--- Record {i+1} ---")
            for col, val in zip(cols, row):
                if isinstance(val, str) and ('<' in val and '>' in val):
                    print(f"{col}: [HTML CONTENT DETECTED - {len(val)} chars]")
                else:
                    print(f"{col}: {val}")
                    
        # Audit layers
        print("\n### LAYERS AUDIT ###")
        cur_p.execute("SELECT laye_id, laye_name_spanish, laye_status, laye_intersection_certificate FROM coa_mae.layers WHERE laye_status AND laye_intersection_certificate")
        layers = cur_p.fetchall()
        print(f"Active Intersection Layers found: {len(layers)}")
        for l in layers:
            print(f"  ID: {l[0]} | Name: {l[1]} | IntCert: {l[3]}")
            
        cur_p.close()
        conn_prod.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    final_validate()
