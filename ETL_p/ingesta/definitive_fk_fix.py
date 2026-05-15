import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL

def definitive_fix():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        print("Applying definitive dimension fixes (ON CONFLICT DO NOTHING)...")
        
        # 1. dim_proyecto
        cur.execute("""
            INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
            VALUES (-1, 'N/A', 'PROYECTO NO ENCONTRADO / HUÉRFANO')
            ON CONFLICT (sk_proyecto) DO NOTHING
        """)
        
        # 2. dim_geografia
        cur.execute("""
            INSERT INTO dw.dim_geografia (sk_geografia, codigo_parroquia, nombre_parroquia)
            VALUES (-1, 'N/A', 'GEOGRAFÍA NO ENCONTRADA')
            ON CONFLICT (sk_geografia) DO NOTHING
        """)
        
        # 3. dim_waste_type (Wait! check column names first)
        try:
            cur.execute("""
                INSERT INTO dw.dim_waste_type (waste_type_key, cawa_id, waste_type_name)
                VALUES (-1, -1, 'TIPO NO DEFINIDO')
                ON CONFLICT (waste_type_key) DO NOTHING
            """)
        except:
            conn.rollback() # Skip if columns mismatch
            
        conn.commit()
        print("Definitive fixes applied successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error in definitive_fix: {e}")

if __name__ == "__main__":
    definitive_fix()
