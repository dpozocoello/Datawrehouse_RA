import psycopg2
from psycopg2.extras import RealDictCursor

def check_locks():
    try:
        conn = psycopg2.connect("host=localhost dbname=dw_reg_v1 user=postgres password=postgres port=5432")
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            pid,
            now() - pg_stat_activity.query_start AS duration,
            query,
            state,
            wait_event_type,
            wait_event
        FROM pg_stat_activity
        WHERE state != 'idle' OR wait_event_type IS NOT NULL
        ORDER BY duration DESC;
        """
        
        cur.execute(query)
        sessions = cur.fetchall()
        
        print("PID        | DURATION        | STATE      | WAIT            | QUERY")
        print("-" * 120)
        for s in sessions:
            pid = str(s['pid'])
            dur = str(s['duration'])
            st = str(s['state'])
            wait = str(s['wait_event'])
            qry = str(s['query'])[:70].replace("\n", " ")
            print(f"{pid:<10} | {dur:<15} | {st:<10} | {wait:<15} | {qry}")
            
        cur.close()
        conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_locks()
