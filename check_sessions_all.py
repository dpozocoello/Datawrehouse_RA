import psycopg2
from psycopg2.extras import RealDictCursor

def check_all_sessions():
    try:
        conn = psycopg2.connect("host=localhost dbname=dw_reg_v1 user=postgres password=postgres port=5432")
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            pid,
            now() - pg_stat_activity.query_start AS duration,
            query,
            state
        FROM pg_stat_activity
        ORDER BY duration DESC;
        """
        
        cur.execute(query)
        sessions = cur.fetchall()
        
        print("PID        | DURATION        | STATE      | QUERY")
        print("-" * 100)
        for s in sessions:
            pid = str(s['pid'])
            dur = str(s['duration'])
            st = str(s['state'])
            qry = str(s['query'])[:60].replace("\n", " ")
            print(f"{pid:<10} | {dur:<15} | {st:<10} | {qry}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_all_sessions()
