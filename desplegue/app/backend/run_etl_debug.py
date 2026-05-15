
import psycopg2

def run_with_notices():
    uri = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
    print("--- Running Chemical ETL with Notice Capture ---")
    
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
        
        # Deploy
        with open('d:/Datawrehouse_RA/sp_etl_chemical_all.sql', 'r', encoding='utf-8') as f:
            sql_sp = f.read()
        cur.execute(sql_sp)
        print("SP Deployed.")
        
        # Execute
        cur.execute("SELECT dw.sp_etl_chemical_all();")
        
        # Print notices
        for notice in conn.notices:
            print(f"NOTICE: {notice.strip()}")
            
        print("Execution finished.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")
        # Even on error, print notices so far
        if 'conn' in locals():
            for notice in conn.notices:
                print(f"NOTICE (on error): {notice.strip()}")

if __name__ == "__main__":
    run_with_notices()
