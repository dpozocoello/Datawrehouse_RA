import psycopg2
import sys

def check_active_sessions():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres"
    }
    
    query = """
    SELECT 
        pid, 
        now() - query_start as duration, 
        wait_event_type, 
        wait_event, 
        state, 
        query 
    FROM pg_stat_activity 
    WHERE state != 'idle' AND pid != pg_backend_pid();
    """
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        print(f"{'PID':>7s} | {'DURATION':15s} | {'WAIT_TYPE':15s} | {'WAIT_EVENT':15s} | {'STATE':10s} | {'QUERY'}")
        print("-" * 120)
        for row in rows:
            print(f"{row[0]:7d} | {str(row[1]):15s} | {str(row[2]):15s} | {str(row[3]):15s} | {row[4]:10s} | {row[5][:100]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_active_sessions()
