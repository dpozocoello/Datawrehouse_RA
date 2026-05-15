
import psycopg2

def apply_and_run():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        print("--- Applying sp_etl_chemical_test.sql ---")
        with open('d:/Datawrehouse_RA/sp_etl_chemical_test.sql', 'r') as f:
            sql = f.read()
            cur.execute(sql)
        conn.commit()
        
        print("--- Executing sp_etl_chemical_test() ---")
        cur.execute("SELECT dw.sp_etl_chemical_test();")
        conn.commit()
        print("SUCCESS")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    apply_and_run()
