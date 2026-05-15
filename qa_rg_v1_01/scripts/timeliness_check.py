import psycopg2
from datetime import datetime
import os

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "utf8"
}

def check_timeliness():
    print("Iniciando Verificación de Oportunidad (Timeliness)...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Consultar última fecha de carga en tablas críticas
        sql = """
            SELECT 'fact_regularizacion', max(fecha_carga) FROM dw.fact_regularizacion
            UNION ALL
            SELECT 'fact_pago', max(fecha_carga) FROM dw.fact_pago
        """
        cur.execute(sql)
        results = cur.fetchall()
        
        report_data = []
        for table, last_load in results:
            if last_load:
                latency = datetime.now() - last_load
                latency_hrs = latency.total_seconds() / 3600
                status = "OK" if latency_hrs <= 24 else "DELAY"
                report_data.append({
                    "Table": table,
                    "Last_Load": last_load.strftime('%Y-%m-%d %H:%M:%S'),
                    "Latency_Hrs": f"{latency_hrs:.2f}",
                    "Status": status
                })
            else:
                report_data.append({
                    "Table": table,
                    "Last_Load": "N/A",
                    "Latency_Hrs": "N/A",
                    "Status": "FAILED"
                })
        
        cur.close()
        conn.close()
        
        # Generar reporte simple
        output_path = "d:\\Datawrehouse_RA\\qa_rg_v1_01\\reports\\timeliness_data.csv"
        with open(output_path, 'w') as f:
            f.write("Table,Last_Load,Latency_Hrs,Status\n")
            for row in report_data:
                f.write(f"{row['Table']},{row['Last_Load']},{row['Latency_Hrs']},{row['Status']}\n")
        
        print(f"Reporte de oportunidad generado: {output_path}")
        for r in report_data:
            print(f" - {r['Table']}: {r['Status']} (Latencia: {r['Latency_Hrs']}h)")
            
    except Exception as e:
        print(f"Error Timeliness: {e}")

if __name__ == "__main__":
    check_timeliness()
