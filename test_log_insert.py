
import psycopg2

def test_insert():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="dw_reg_v1"
        )
        conn.autocommit = True
        cur = conn.cursor()
        print("Connected to database.")
        
        cur.execute("INSERT INTO dw.etl_process_log (process_name, status, start_time) VALUES ('Test Manual Execution', 'SUCCESS', now()) RETURNING id;")
        new_id = cur.fetchone()[0]
        print(f"Inserted row with ID: {new_id}")
        
        cur.close()
        conn.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_insert()
