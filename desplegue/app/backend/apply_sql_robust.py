import psycopg2
import sys

def apply_sql_robust(file_path):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Datawarehouse_RA",
            user="postgres",
            password="postgres",
            port=5432
        )
        conn.set_client_encoding('LATIN1')
        cur = conn.cursor()
        
        # Try different encodings for reading the SQL file
        sql = None
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    sql = f.read()
                print(f"Read {file_path} with {enc}")
                break
            except:
                continue
        
        if sql is None:
            print(f"Failed to read {file_path} with any encoding")
            return

        print(f"Applying SQL from {file_path}...")
        cur.execute(sql)
        conn.commit()
        print("Success.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error applying {file_path}: {e}")

if __name__ == "__main__":
    for f in sys.argv[1:]:
        apply_sql_robust(f)
