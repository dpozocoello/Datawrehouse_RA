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

with open("d:\\Datawrehouse_RA\\verify_stg.txt", "w") as f:
    f.write("--- Case 1: MAE-RA-2015-220472 (ware_id 10578) in STG ---\n")
    query1 = "SELECT waste_generator_id, lp_id_proyect, lp_prco_id FROM stg.stg_fact_waste_generation WHERE waste_generator_id = 10578 LIMIT 5"
    cols, rows = run_query(query1)
    f.write(f"Result: {rows}\n")

    f.write("\n--- Case 2: MAATE-RA-2024-519793 (ware_id 10568) in STG ---\n")
    query2 = "SELECT waste_generator_id, lp_id_proyect, lp_prco_id FROM stg.stg_fact_waste_generation WHERE waste_generator_id = 10568 LIMIT 5"
    cols, rows = run_query(query2)
    f.write(f"Result: {rows}\n")

    f.write("\n--- stg_rgd_project_mapping Check ---\n")
    query3 = "SELECT * FROM stg.stg_rgd_project_mapping WHERE ware_id IN (10578, 10568)"
    cols, rows = run_query(query3)
    f.write(f"Mapping: {rows}\n")
