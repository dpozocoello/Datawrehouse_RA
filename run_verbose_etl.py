
import psycopg2
import traceback

def run_verbose():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="dw_reg_v1"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("--- Running Unified Chemical ETL (Verbose) ---")
        with open('d:/Datawrehouse_RA/etl_chemical_imports_load.sql', 'r') as f:
            sql = f.read()
            
        cur.execute(sql)
        print("SUCCESS from Python's perspective.")
        
        cur.close()
        conn.close()
    except Exception:
        print("--- Python EXC traceback ---")
        traceback.print_exc()

if __name__ == "__main__":
    run_verbose()
