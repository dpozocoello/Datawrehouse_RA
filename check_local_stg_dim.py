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

with open("d:\\Datawrehouse_RA\\query_local_2.txt", "w") as f:
    f.write("--- Checking stg_fact_waste_generation for RGD 10578 ---\n")
    query_stg = "SELECT project_code, project_id, waste_generator_id FROM stg.stg_fact_waste_generation WHERE waste_generator_id = 10578 LIMIT 5"
    cols, rows = run_query(query_stg)
    f.write(f"Stg Columns: {cols}\n")
    for r in rows:
        f.write(f"{r}\n")

    f.write("\n--- Checking dim_proyecto for sk_proyecto 57982 ---\n")
    query_dim = "SELECT sk_proyecto, codigo_proyecto FROM dw.dim_proyecto WHERE sk_proyecto = 57982"
    cols, rows = run_query(query_dim)
    f.write(f"Dim Result: {rows}\n")
