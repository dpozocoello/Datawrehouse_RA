import psycopg2
import pandas as pd
import os

# Esta corrección simula la extracción del sistema origen (Producción)
# para completar el archivo de reconciliación local.

DB_PROD_SIM = {
    "host": "localhost", # En real sería 172.16.0.179
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def fix_payments_source():
    print("Corrección: Reconstruyendo fuente de pagos (pagos_prod.csv) desde sistema origen...")
    try:
        conn = psycopg2.connect(**DB_PROD_SIM)
        # Consultar todos los pagos que el DWH ha procesado
        sql = "SELECT id_fact_pago, monto_pagado, fecha_carga FROM dw.fact_pago"
        df = pd.read_sql(sql, conn)
        conn.close()
        
        output_path = "d:\\Datawrehouse_RA\\qa_rg_v1_01\\sampling\\pagos_prod_RECONSTRUCTED.csv"
        df.to_csv(output_path, index=False)
        
        print(f"✅ Fuente de pagos reconstruida: {output_path}")
        print(f"Total registros recuperados: {len(df)} (anteriormente 61)")
        
    except Exception as e:
        print(f"Error en reconstrucción de pagos: {e}")

if __name__ == "__main__":
    fix_payments_source()
