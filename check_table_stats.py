import psycopg2
from psycopg2.extras import RealDictCursor

def check_table_stats():
    try:
        conn = psycopg2.connect("host=localhost dbname=dw_reg_v1 user=postgres password=postgres port=5432")
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT COUNT(*) FROM dw.fact_pago")
        count = cur.fetchone()['count']
        print(f"Total registros en dw.fact_pago: {count}")
        
        cur.execute("SELECT COUNT(*) FROM dw.fact_pago WHERE numero_tramite IS NULL")
        null_count = cur.fetchone()['count']
        print(f"Registros sin numero_tramite (SUIA): {null_count}")

        cur.execute("SELECT COUNT(*) FROM dw.fact_pago WHERE secuencia_pago IS NOT NULL")
        seq_count = cur.fetchone()['count']
        print(f"Registros ya procesados (secuencia_pago IS NOT NULL): {seq_count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_table_stats()
