import psycopg2
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_SUIA_ENLISY

def run_query(query):
    conn = psycopg2.connect(
        host=CONN_SUIA_ENLISY['host'],
        port=CONN_SUIA_ENLISY['port'],
        user=CONN_SUIA_ENLISY['user'],
        password=CONN_SUIA_ENLISY['password'],
        database=CONN_SUIA_ENLISY['database']
    )
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return cols, rows

with open("d:\\Datawrehouse_RA\\query_results_3.txt", "w") as f:
    f.write("--- Example 2: ware_id = 10568 ---\n")
    query_m = "SELECT wapr_id, ware_id, prco_id, id_proyect, wapr_description_system FROM coa_waste_generator_record.waste_generator_record_project_licencing_coa WHERE ware_id = 10568"
    cols, rows = run_query(query_m)
    f.write(f"Columns: {cols}\n")
    for r in rows:
        f.write(f"{r}\n")
