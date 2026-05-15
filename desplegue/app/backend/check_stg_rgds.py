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

with open("d:\\Datawrehouse_RA\\query_local_4.txt", "w") as f:
    f.write("--- Finding all RGDs for project MAE-RA-2015-220472 in STG ---\n")
    query = "SELECT project_code, waste_generator_id, count(*) FROM stg.stg_fact_waste_generation WHERE project_code = 'MAE-RA-2015-220472' GROUP BY 1, 2"
    cols, rows = run_query(query)
    f.write(f"Result: {rows}\n")
