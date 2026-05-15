import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def list_pids():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        cur.execute("SELECT pid, query, state, now() - query_start FROM pg_stat_activity WHERE state != 'idle'")
        rows = cur.fetchall()
        print("Active PIDs:")
        for pid, query, state, duration in rows:
            print(f"PID: {pid} | State: {state} | Duration: {duration} | Query: {query[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    list_pids()
