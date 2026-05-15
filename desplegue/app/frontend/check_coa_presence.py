import psycopg2

def run_raw_diag():
    try:
        conn = psycopg2.connect(dbname="dwh_bi", user="postgres", password="postgres", host="localhost")
        conn.set_client_encoding('LATIN1')
        cur = conn.cursor()
        
        # 1. Buscar un ejemplo de 'COA' en la dimensión y ver sus bytes
        cur.execute("SELECT generator_type::bytea, COUNT(*) FROM dw.dim_waste_generator GROUP BY 1")
        types = cur.fetchall()
        
        # 2. Buscar si hay CUALQUIER registro en Fact que apunte a un generador cuyo tipo sea 'COA'
        cur.execute("""
            SELECT COUNT(*) 
            FROM dw.fact_waste_generation f
            JOIN dw.dim_waste_generator w ON f.waste_generator_key = w.waste_generator_key
            WHERE w.generator_type ILIKE '%COA%'
        """)
        linked_coa = cur.fetchone()[0]

        with open('coa_raw_results.txt', 'w', encoding='utf-8') as f:
            f.write("=== ANALISIS DE BYTES - TIPO GENERADOR ===\n")
            for t in types:
                f.write(f"Tipo (Bytes): {t[0].hex()} | Cantidad: {t[1]}\n")
            
            f.write(f"\nFact Records vinculados a %COA%: {linked_coa}\n")
            
        print("Hecho.")
    except Exception as e:
        with open('coa_raw_error.txt', 'w', encoding='utf-8') as f:
            f.write(str(e))
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_raw_diag()
