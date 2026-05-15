import psycopg2
import sys
import os

sys.path.insert(0, r'/opt/eco-sieaa/etl')
from config import CONN_DWH_LOCAL

def verify_coherence():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        
        # 1. Audit COA vs RCOA (using project code patterns in dw.fact_waste_generation)
        query = """
        SELECT 
            CASE WHEN p.codigo_proyecto LIKE 'MAE-RA-2016-%' THEN 'COA (LEGADO)' ELSE 'RCOA (NUEVO)' END as sistema,
            COUNT(*) as total_hechos,
            SUM(CASE WHEN f.geo_location_key IS NULL THEN 1 ELSE 0 END) as sin_geo,
            SUM(CASE WHEN f.waste_type_key IS NULL THEN 1 ELSE 0 END) as sin_tipo_desecho,
            SUM(CASE WHEN f.dangerous_waste_key IS NULL THEN 1 ELSE 0 END) as sin_clase_peligrosa
        FROM dw.fact_waste_generation f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        GROUP BY 1
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        print("====================================================")
        print("COHETRENCIA DE DATOS: COA VS RCOA (DWH Audit)")
        print("====================================================")
        for row in rows:
            print(f"Sistema: {row[0]}")
            print(f"  Total Hechos: {row[1]:,}")
            print(f"  Sin Geografía: {row[2]:,} ({(row[2]/row[1])*100:.1f}%)")
            print(f"  Sin Tipo Desecho: {row[3]:,}")
            print(f"  Sin Clase Peligrosa: {row[4]:,} ({(row[4]/row[1])*100:.1f}%)")
        print("====================================================")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_coherence()
