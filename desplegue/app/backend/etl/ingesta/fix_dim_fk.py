import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def fix_fk():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        print("Inserting missing -1 records for dimensions...")
        
        # 1. dim_proyecto
        cur.execute("""
            INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
            SELECT -1, 'N/A', 'PROYECTO NO ENCONTRADO / HUÉRFANO'
            WHERE NOT EXISTS (SELECT 1 FROM dw.dim_proyecto WHERE sk_proyecto = -1)
        """)
        
        # 2. dim_geografia
        cur.execute("""
            INSERT INTO dw.dim_geografia (sk_geografia, codigo_parroquia, nombre_parroquia)
            SELECT -1, 'N/A', 'GEOGRAFÍA NO ENCONTRADA'
            WHERE NOT EXISTS (SELECT 1 FROM dw.dim_geografia WHERE sk_geografia = -1)
        """)
        
        # 3. dim_area
        cur.execute("""
            INSERT INTO dw.dim_area (sk_area, area_nombre)
            SELECT -1, 'ÁREA NO DEFINIDA'
            WHERE NOT EXISTS (SELECT 1 FROM dw.dim_area WHERE sk_area = -1)
        """)
        
        conn.commit()
        print("All missing records created successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error in fix_fk: {e}")

if __name__ == "__main__":
    fix_fk()
