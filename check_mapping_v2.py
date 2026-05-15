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

with open("d:\\Datawrehouse_RA\\query_results_2.txt", "w") as f:
    f.write("--- Example 2: MAATE-RA-2024-519793 ---\n")
    query_p = "SELECT prco_id, prco_cua FROM coa_mae.project_licencing_coa WHERE prco_cua = 'MAATE-RA-2024-519793'"
    cols, rows = run_query(query_p)
    f.write(f"Project: {rows}\n")

    query_m = "SELECT * FROM coa_waste_generator_record.waste_generator_record_project_licencing_coa WHERE id_proyect = 449186"
    cols, rows = run_query(query_m)
    f.write(f"Mapping for ID 449186: {rows}\n")

    f.write("\n--- Example 1: MAE-RA-2015-220472 (Re-check) ---\n")
    query_p1 = "SELECT prco_id, prco_cua FROM coa_mae.project_licencing_coa WHERE prco_cua LIKE '%220472'"
    cols, rows = run_query(query_p1)
    f.write(f"Project 1 (Suffix 220472): {rows}\n")

    query_m1 = "SELECT * FROM coa_waste_generator_record.waste_generator_record_project_licencing_coa WHERE ware_id = 10578"
    cols, rows = run_query(query_m1)
    f.write(f"Mapping for ware_id 10578: {rows}\n")
