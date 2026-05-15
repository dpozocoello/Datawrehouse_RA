import psycopg2
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_DWH_LOCAL

def run_sql_file(file_path):
    conn = psycopg2.connect(
        host=CONN_DWH_LOCAL['host'],
        port=CONN_DWH_LOCAL['port'],
        user=CONN_DWH_LOCAL['user'],
        password=CONN_DWH_LOCAL['password'],
        database=CONN_DWH_LOCAL['database']
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"Executing {file_path}...")
    try:
        cur.execute(sql)
        print("Execution successful!")
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    sql_file = "d:\\Datawrehouse_RA\\etl_waste_chemical_load.sql"
    run_sql_file(sql_file)
