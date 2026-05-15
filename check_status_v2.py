
import psycopg2

def check_counts_and_logs():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        print("--- Log Status (Last 3) ---")
        cur.execute("SELECT id, process_name, status, start_time, rows_inserted FROM dw.etl_process_log ORDER BY id DESC LIMIT 3;")
        for row in cur.fetchall():
            print(f"ID {row[0]}: {row[1]} | Status: {row[2]} | Start: {row[3]} | Rows: {row[4]}")
            
        print("\n--- Fact Table Counts ---")
        tables = ['dw.fact_chemical_import', 'dw.fact_chemical_movement', 'dw.fact_chemical_declaration']
        for table in tables:
            cur.execute(f"SELECT count(*) FROM {table};")
            print(f"{table}: {cur.fetchone()[0]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_counts_and_logs()
