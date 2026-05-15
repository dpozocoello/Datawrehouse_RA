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

with open("d:\\Datawrehouse_RA\\query_local_1.txt", "w") as f:
    f.write("--- Checking RGD 10578 in Local DWH ---\n")
    query = """
    SELECT f.sk_proyecto, p.codigo_proyecto, g.waste_generator_id, g.generator_name 
    FROM dw.fact_waste_generation f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_waste_generator g ON f.waste_generator_key = g.waste_generator_key
    WHERE g.waste_generator_id = 10578
    """
    cols, rows = run_query(query)
    f.write(f"Result: {rows}\n")
