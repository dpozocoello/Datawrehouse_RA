
import psycopg2

def check_progress():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        cur = conn.cursor()
        cur.execute("SELECT id, status, start_time, rows_inserted FROM dw.etl_process_log ORDER BY id DESC LIMIT 1;")
        res = cur.fetchone()
        if res:
            print(f"Current Log: ID {res[0]} | Status: {res[1]} | Start: {res[2]} | Rows: {res[3]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_progress()
