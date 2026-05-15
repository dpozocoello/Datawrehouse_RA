
import psycopg2

def run_direct():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        conn.autocommit = True
        cur = conn.cursor()
        print("--- Calling sp_etl_chemical_all() DIRECTLY ---")
        cur.execute("SELECT dw.sp_etl_chemical_all();")
        print("DONE.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Postgres Error: {e}")

if __name__ == "__main__":
    run_direct()
