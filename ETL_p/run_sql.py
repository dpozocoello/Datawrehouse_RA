import psycopg2
from config import CONN_DWH_LOCAL

def run_ddl(file_path):
    print(f"Executing DDL: {file_path}")
    conn = psycopg2.connect(**CONN_DWH_LOCAL)
    cur = conn.cursor()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        cur.execute(sql)
        conn.commit()
        print("DDL executed successfully.")
    except Exception as e:
        print(f"Error executing DDL: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_ddl(sys.argv[1])
    else:
        print("Please provide a file path.")
