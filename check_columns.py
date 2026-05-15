import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))

from config import CONN_DWH_LOCAL
from connections import get_connection

def check_cols(schema, table):
    try:
        with get_connection(CONN_DWH_LOCAL) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema}' 
                      AND table_name = '{table}';
                """)
                rows = cur.fetchall()
                print(f"Columns in {schema}.{table}:")
                for r in rows:
                    print(f" - {r[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python check_columns.py <schema> <table>")
    else:
        check_cols(sys.argv[1], sys.argv[2])
