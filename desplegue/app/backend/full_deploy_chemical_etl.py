
import psycopg2
import os

def deploy_and_run():
    uri = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
    print("--- Deploying and Running Chemical ETL ---")
    
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
        
        # 1. Update/Create the stored procedure
        sql_sp_path = 'd:/Datawrehouse_RA/sp_etl_chemical_all.sql'
        print(f"Reading {sql_sp_path}...")
        with open(sql_sp_path, 'r', encoding='utf-8') as f:
            sql_sp = f.read()
        
        print("Creating/Updating stored procedure...")
        cur.execute(sql_sp)
        print("Stored procedure updated.")
        
        # 2. Run the stored procedure
        print("Executing dw.sp_etl_chemical_all()... This may take a moment.")
        cur.execute("SELECT dw.sp_etl_chemical_all();")
        print("ETL Execution completed successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    deploy_and_run()
