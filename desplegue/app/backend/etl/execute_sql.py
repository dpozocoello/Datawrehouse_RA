import sys
import os
import psycopg2

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL

def execute_sql_file(file_path):
    print(f"Executing {file_path}...")
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        # Ejecutar el SQL (split por ';' para ver progreso si es necesario, pero simple es mejor aquí)
        cur.execute(sql)
        print("SQL executed successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR executing SQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python execute_sql.py <path_to_sql_file>")
        sys.exit(1)
    execute_sql_file(sys.argv[1])
