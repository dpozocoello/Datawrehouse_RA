import psycopg2
import sys

def apply_remote_sql(file_path):
    print(f"Applying to 172.16.0.179: {file_path}...")
    try:
        conn = psycopg2.connect(
            host="172.16.0.179",
            database="suia_enlisy",
            user="postgres",
            password="postgres",
            port=5632
        )
        conn.set_client_encoding('LATIN1')
        cur = conn.cursor()
        
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
    for f in sys.argv[1:]:
        apply_remote_sql(f)
