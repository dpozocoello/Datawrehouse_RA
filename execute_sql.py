
import psycopg2
import sys

def execute_file(filepath):
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
            cur.execute(sql)
        conn.commit()
        print(f"Successfully executed {filepath}")
        conn.close()
    except Exception as e:
        print(f"Error executing {filepath}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        execute_file(sys.argv[1])
    else:
        print("Usage: python execute_sql.py <filepath>")
