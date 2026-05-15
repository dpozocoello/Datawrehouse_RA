import psycopg2
from psycopg2.extras import RealDictCursor

def check_data_volumes():
    try:
        conn = psycopg2.connect("host=localhost dbname=dw_reg_v1 user=postgres password=postgres port=5432")
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT COUNT(*) FROM dw.fact_regularizacion")
        reg_count = cur.fetchone()['count']
        print(f"Total registros en dw.fact_regularizacion: {reg_count}")
        
        cur.execute("SELECT COUNT(*) FROM dw.fact_pago")
        pago_count = cur.fetchone()['count']
        print(f"Total registros en dw.fact_pago: {pago_count}")

        cur.execute("SELECT origen, COUNT(*) FROM dw.fact_pago GROUP BY 1")
        origen_counts = cur.fetchall()
        for oc in origen_counts:
            print(f"Origen {oc['origen']}: {oc['count']} registros")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data_volumes()
