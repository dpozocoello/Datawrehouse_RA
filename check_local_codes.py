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
    cols = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return cols, rows

with open("d:\\Datawrehouse_RA\\query_local_3.txt", "w") as f:
    f.write("--- Distinct Project Codes for RGD 10578 in STG ---\n")
    query = "SELECT project_code, count(*) FROM stg.stg_fact_waste_generation WHERE waste_generator_id = 10578 GROUP BY 1"
    cols, rows = run_query(query)
    f.write(f"Result: {rows}\n")
