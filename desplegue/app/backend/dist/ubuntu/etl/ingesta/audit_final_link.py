import psycopg2
import sys
import os

sys.path.insert(0, r'/opt/eco-sieaa/etl')
from config import CONN_DWH_LOCAL

def audit_final_link():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        
        # 1. Buscar proyecto 495449 por codigo
        cur.execute("SELECT sk_proyecto, codigo_proyecto FROM dw.dim_proyecto WHERE codigo_proyecto LIKE '%495449%' OR nombre_proyecto LIKE '%495449%'")
        projs = cur.fetchall()
        print(f"Projects found matching 495449: {projs}")
        
        # 2. Buscar intersección para esos proyectos
        if projs:
            p_ids = [p[0] for p in projs]
            cur.execute("SELECT sk_proyecto, certificate_code, LEFT(html_location, 50) FROM dw.dim_intersection WHERE sk_proyecto IN %s", (tuple(p_ids),))
            links = cur.fetchall()
            print(f"Links found in dim_intersection: {links}")
        
        # 3. Validar record 2025-02315 directamente
        cur.execute("SELECT sk_proyecto, certificate_code FROM dw.dim_intersection WHERE certificate_code = 'MAATE-SUIA-RA-DZDG-2025-02315'")
        cert = cur.fetchone()
        print(f"Certificate 2025-02315 found: {cert}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    audit_final_link()
