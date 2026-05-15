import psycopg2
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_DWH_LOCAL

def run_query(query):
    conn = psycopg2.connect(
        host=CONN_DWH_LOCAL['host'],
        port=CONN_DWH_LOCAL['port'],
        user=CONN_DWH_LOCAL['user'],
        password=CONN_DWH_LOCAL['password'],
        database=CONN_DWH_LOCAL['database']
    )
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

if __name__ == "__main__":
    count = run_query("SELECT count(*) FROM dw.fact_waste_generation")[0][0]
    print(f"Current count in dw.fact_waste_generation: {count}")
    
    stg_count = run_query("SELECT count(*) FROM stg.stg_fact_waste_generation")[0][0]
    print(f"Total rows in stg.stg_fact_waste_generation: {stg_count}")
