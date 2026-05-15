import sys
import os

# Add ETL_p to path to use connections
sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))

from config import CONN_DWH_LOCAL
from connections import get_connection

def run_sql_file(file_path):
    print(f"Reading SQL file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split by ; but be careful with DO blocks and FUNCTIONS.
    # Actually, let's just run the whole thing in one go if possible, 
    # or use a more robust splitting.
    # PostgreSQL can handle multiple statements in one execute call 
    # as long as they are separated by ;.

    try:
        with get_connection(CONN_DWH_LOCAL, autocommit=True) as conn:
            with conn.cursor() as cur:
                print("Connected. Executing SQL...")
                cur.execute(sql)
                if cur.description:
                    colnames = [desc[0] for desc in cur.description]
                    print(" | ".join(colnames))
                    print("-" * 50)
                    for row in cur.fetchall():
                        print(" | ".join(map(str, row)))
                print("SQL executed successfully.")
    except Exception as e:
        print(f"Error executing SQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply_sql.py <file_path>")
        sys.exit(1)
    
    run_sql_file(sys.argv[1])
