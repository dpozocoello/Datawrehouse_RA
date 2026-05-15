import psycopg2
from psycopg2.extras import RealDictCursor

def check_distribution():
    try:
        conn = psycopg2.connect("host=localhost dbname=dw_reg_v1 user=postgres password=postgres port=5432")
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT COUNT(DISTINCT numero_tramite) FROM dw.fact_pago WHERE numero_tramite IS NOT NULL")
        distinct_tramites = cur.fetchone()['count']
        print(f"Trámites únicos: {distinct_tramites}")
        
        cur.execute("""
            SELECT AVG(cnt) as avg_p_tramite, MAX(cnt) as max_p_tramite
            FROM (SELECT COUNT(*) as cnt FROM dw.fact_pago GROUP BY numero_tramite) s
        """)
        stats = cur.fetchone()
        print(f"Pagos promedio por trámite: {stats['avg_p_tramite']}")
        print(f"Pagos máximos por trámite: {stats['max_p_tramite']}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_distribution()
