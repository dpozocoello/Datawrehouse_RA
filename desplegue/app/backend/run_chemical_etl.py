
import sys
import os
import psycopg2

def run_chemical_etl():
    print("--- Executing Unified Chemical ETL (sp_etl_chemical_all) ---")
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
        
        # Load SQL
        sql_path = 'd:/Datawrehouse_RA/etl_chemical_imports_load.sql'
        with open(sql_path, 'r') as f:
            sql = f.read()
            
        print("Running SQL...")
        cur.execute(sql)
        print("ETL Step executed.")
        
        # Verify Results
        print("\n--- Verifying Consistency Results ---")
        cur.execute("""
            SELECT 
                CASE WHEN sk_proyecto = 0 THEN 'Orphan (SK 0)' ELSE 'Linked' END as status,
                count(*)
            FROM dw.fact_chemical_import
            GROUP BY 1;
        """)
        print("fact_chemical_import status:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
            
        cur.execute("""
            SELECT 
                CASE WHEN sk_proyecto = 0 THEN 'Orphan (SK 0)' ELSE 'Linked' END as status,
                count(*)
            FROM dw.fact_chemical_declaration
            GROUP BY 1;
        """)
        print("fact_chemical_declaration status:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_chemical_etl()
