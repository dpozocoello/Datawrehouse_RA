import psycopg2
import sys

def apply_sql_robust(file_path):
    print(f"Applying {file_path}...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dw_reg_v1",
            user="postgres",
            password="postgres",
            port=5432
        )
        conn.set_client_encoding('LATIN1')
        cur = conn.cursor()
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            sql = f.read()
            
        cur.execute(sql)
        conn.commit()
        print(f"SUCCESS: {file_path}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"FAILED {file_path}: {repr(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    for f in sys.argv[1:]:
        apply_sql_robust(f)
