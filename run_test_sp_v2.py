
import psycopg2
import sys

def apply_and_run():
    log_file = 'd:/Datawrehouse_RA/test_sp_error.log'
    with open(log_file, 'w') as log:
        try:
            conn = psycopg2.connect(
                host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
            )
            cur = conn.cursor()
            
            log.write("--- Applying sp_etl_chemical_test.sql ---\n")
            with open('d:/Datawrehouse_RA/sp_etl_chemical_test.sql', 'r') as f:
                sql = f.read()
                cur.execute(sql)
            conn.commit()
            
            log.write("--- Executing sp_etl_chemical_test() ---\n")
            cur.execute("SELECT dw.sp_etl_chemical_test();")
            conn.commit()
            log.write("SUCCESS\n")
            print("SUCCESS")
            
            cur.close()
            conn.close()
        except Exception as e:
            log.write(f"ERROR: {str(e)}\n")
            print(f"ERROR: {e}")

if __name__ == "__main__":
    apply_and_run()
