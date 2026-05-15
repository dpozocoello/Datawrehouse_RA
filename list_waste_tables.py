import psycopg2
import sys
import os

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_SUIA_ENLISY

def list_tables_in_schema(schema_name):
    conn = psycopg2.connect(
        host=CONN_SUIA_ENLISY['host'],
        port=CONN_SUIA_ENLISY['port'],
        user=CONN_SUIA_ENLISY['user'],
        password=CONN_SUIA_ENLISY['password'],
        database=CONN_SUIA_ENLISY['database']
    )
    cur = conn.cursor()
    query = f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{schema_name}'
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]

if __name__ == "__main__":
    try:
        tables = list_tables_in_schema('waste_dangerous')
        print(f"Tables in waste_dangerous: {tables}")
    except Exception as e:
        print(f"Error: {e}")
