import psycopg2
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_DWH_LOCAL

def clear_locks():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Encontrar TODOS los PIDs en la base de datos destino
        query = """
        SELECT pid, query 
        FROM pg_stat_activity 
        WHERE datname = 'dw_reg_v1' 
          AND pid <> pg_backend_pid()
        """
        cur.execute(query)
        blockers = cur.fetchall()
        
        for pid, q in blockers:
            print(f"Terminating PID {pid}...")
            cur.execute(f"SELECT pg_terminate_backend({pid})")
        
        print(f"Cleared {len(blockers)} potential blockers.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_locks()
