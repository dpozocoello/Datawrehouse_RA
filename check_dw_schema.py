import psycopg2
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_DWH_LOCAL

def get_columns(table_name):
    conn = psycopg2.connect(
        host=CONN_DWH_LOCAL['host'],
        port=CONN_DWH_LOCAL['port'],
        user=CONN_DWH_LOCAL['user'],
        password=CONN_DWH_LOCAL['password'],
        database=CONN_DWH_LOCAL['database']
    )
    cur = conn.cursor()
    query = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = 'dw' AND table_name = '{table_name}'
        ORDER BY ordinal_position
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

if __name__ == "__main__":
    try:
        cols = get_columns('dim_waste_generator')
        print(f"Columns in dw.dim_waste_generator:")
        for c in cols:
            print(c)
    except Exception as e:
        print(f"Error: {e}")
