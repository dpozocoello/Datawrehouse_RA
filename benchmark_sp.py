import psycopg2
import time

def benchmark_sp():
    conn = psycopg2.connect("host=localhost dbname=dw_reg_v1 user=postgres password=postgres port=5432")
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Iniciando benchmark de dw.sp_calcular_secuencia_pagos()...")
    start_time = time.time()
    
    cur.execute("SELECT dw.sp_calcular_secuencia_pagos();")
    
    end_time = time.time()
    
    # Imprimir notices capturados al final
    for notice in conn.notices:
        print(f"NOTICE: {notice.strip()}")
        
    print(f"Benchmark completado en {end_time - start_time:.4f} segundos.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    benchmark_sp()
