import psycopg2
import sys

def extract_discrepancies():
    try:
        conn = psycopg2.connect(dbname="dwh_bi", user="postgres", password="postgres", host="localhost")
        cur = conn.cursor()
        
        # Consultar como bytes (bytea) para evitar el decode automático de psycopg2
        query = """
        SELECT DISTINCT provincia::bytea
        FROM dw.dim_area 
        WHERE sk_area > 0 
          AND provincia NOT IN (SELECT nombre_provincia FROM ref.inec_dpa_2024) 
          AND provincia != 'N/A'
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        print(f"Detectadas {len(rows)} discrepancias (como bytes).")
        
        with open('D:\\DashboardRA\\QA_Suite\\HALLAZGOS_PROVINCIAS.txt', 'w', encoding='utf-8') as f:
            f.write("PROVINCIAS CON DISCREPANCIA (RAW BYTES):\n")
            f.write("-" * 40 + "\n")
            for r in rows:
                raw_bytes = bytes(r[0])
                # Intentar decodificar con reemplazo para ver qué hay ahí
                decoded = raw_bytes.decode('utf-8', errors='replace')
                f.write(f"{decoded} (Hex: {raw_bytes.hex()})\n")
                    
        print(f"Éxito: Detalles guardados en QA_Suite\\HALLAZGOS_PROVINCIAS.txt")
        
    except Exception as e:
        print(f"Error detectado: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    extract_discrepancies()
