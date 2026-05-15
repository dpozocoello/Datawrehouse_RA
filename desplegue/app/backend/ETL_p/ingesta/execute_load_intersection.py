import os
import sys

# Configuración de rutas dinámica
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL, PROJECT_ROOT

def execute_load():
    try:
        # ... (conexión)
        sql_path = os.path.join(PROJECT_ROOT, "etl_intersection_load.sql")
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        print("Executing etl_intersection_load.sql...")
        cur.execute(sql)
        conn.commit()
        print("Load executed successfully.")
        
        # Validation
        cur.execute("SELECT count(*) FROM dw.dim_intersection")
        count = cur.fetchone()[0]
        print(f"Total SNAP Certificates in dw.dim_intersection: {count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    execute_load()
