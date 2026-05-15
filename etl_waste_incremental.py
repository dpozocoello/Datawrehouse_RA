import sys
import os
import time
from datetime import datetime

# Add ETL_p to path to use connections
sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))

from config import CONN_DWH_LOCAL
from connections import get_connection

def run_incremental_etl(mode='INCREMENTAL'):
    print(f"--- Starting Waste ETL in {mode} mode ---")
    
    try:
        with get_connection(CONN_DWH_LOCAL, autocommit=True) as conn:
            with conn.cursor() as cur:
                # 1. Handle Full Refresh (Truncate before the DO block if requested)
                if mode == 'FULL':
                    print("Performing FULL TRUNCATE...")
                    cur.execute("TRUNCATE TABLE dw.fact_waste_generation CASCADE")
                
                # 2. Load SQL Content (which now handles its own logging)
                sql_path = os.path.join(os.getcwd(), "etl_waste_chemical_load.sql")
                with open(sql_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # 3. Execute SQL
                print("Executing Autonomous Transformation SQL...")
                cur.execute(sql_content)
                
                print(f"ETL Execution Finished for {mode} mode.")
                print("Check 'dw.etl_process_log' for detailed metrics.")
                
    except Exception as e:
        print(f"CRITICAL ERROR in ETL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    mode = 'INCREMENTAL'
    if len(sys.argv) > 1:
        if sys.argv[1].upper() == '--FULL':
            mode = 'FULL'
            
    run_incremental_etl(mode)
