import psycopg2
import sys

try:
    # Forzar codificación LATIN1 a nivel de conexión psycopg2
    conn = psycopg2.connect(dbname="dwh_bi", user="postgres", password="postgres", host="localhost")
    conn.set_client_encoding('LATIN1')
    cur = conn.cursor()
    
    query = """
    SELECT DISTINCT provincia 
    FROM dw.dim_area 
    WHERE sk_area > 0 
      AND provincia NOT IN (SELECT nombre_provincia FROM ref.inec_dpa_2024) 
      AND provincia != 'N/A'
    """
    cur.execute(query)
    rows = cur.fetchall()
    
    with open('inconsistent_provinces.txt', 'w', encoding='utf-8') as f:
        f.write("--- Provincias Inconsistentes Detectadas ---\n")
        if not rows:
            f.write("No se detectaron inconsistencias.\n")
        else:
            for r in rows:
                # Intentar limpiar el dato si es necesario
                val = r[0]
                f.write(f"{val}\n")
    print("Resultados guardados en inconsistent_provinces.txt")
    
except Exception as e:
    with open('dq_debug_error.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error Final: {str(e)}")
    print("Error crítico guardado en dq_debug_error.txt")
finally:
    if 'conn' in locals():
        conn.close()
