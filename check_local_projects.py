
import psycopg2
import sys

def check_local():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        print("--- Local Projects Count by System ---")
        cur.execute("SELECT sistema, count(*) FROM dw.dim_proyecto GROUP BY sistema ORDER BY 2 DESC;")
        rows = cur.fetchall()
        for row in rows:
            print(f"System: {row[0]} | Count: {row[1]}")
            
        print("\n--- Project Mapping Check (stg.stg_project_mapping) ---")
        cur.execute("SELECT count(*) FROM stg.stg_project_mapping;")
        print(f"Total entries in stg_project_mapping: {cur.fetchone()[0]}")
        
        print("\n--- Chemical Staging Check ---")
        cur.execute("SELECT count(*) FROM stg.stg_chemical_sustances_records;")
        print(f"Total in stg_chemical_sustances_records: {cur.fetchone()[0]}")
        
        cur.execute("SELECT count(*) FROM stg.stg_import_request;")
        print(f"Total in stg_import_request: {cur.fetchone()[0]}")
        
        cur.execute("SELECT count(prco_id) as linked, count(*) - count(prco_id) as nulls FROM stg.stg_chemical_sustances_records;")
        linked, nulls = cur.fetchone()
        print(f"Staging Links: {linked} linked, {nulls} NULL prco_id")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_local()
