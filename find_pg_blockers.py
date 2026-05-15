import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def find_blockers():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        print("Searching for blockers in PostgreSQL...")
        cur.execute("""
            SELECT
                blocked_locks.pid AS blocked_pid,
                blocked_activity.query AS blocked_query,
                blocking_locks.pid AS blocking_pid,
                blocking_activity.query AS blocking_query,
                now() - blocking_activity.query_start AS blocking_duration
            FROM pg_catalog.pg_locks blocked_locks
            JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_locks.pid = blocked_activity.pid
            JOIN pg_catalog.pg_locks blocking_locks
                ON blocking_locks.locktype = blocked_locks.locktype
                AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                AND blocking_locks.pid != blocked_locks.pid
            JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_locks.pid = blocking_activity.pid
            WHERE NOT blocked_locks.granted;
        """)
        blockers = cur.fetchall()
        if not blockers:
            print("No blockers found.")
        for b_pid, b_query, bl_pid, bl_query, duration in blockers:
            print(f"\nBlocked PID: {b_pid}")
            print(f"Blocked Query: {b_query[:100]}...")
            print(f"Blocking PID: {bl_pid}")
            print(f"Blocking Query: {bl_query[:100]}...")
            print(f"Blocking Duration: {duration}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    find_blockers()
