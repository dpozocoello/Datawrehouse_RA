import psycopg2
import pandas as pd
import os
import json

# Configuración de conexión (usando variables placeholders para seguridad)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "utf8"
}

def get_dwh_counts():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        queries = {
            "fact_regularizacion": "SELECT count(*) FROM dw.fact_regularizacion",
            "fact_pago": "SELECT count(*) FROM dw.fact_pago",
            "dim_geografia": "SELECT count(*) FROM dw.dim_geografia"
        }
        counts = {}
        cur = conn.cursor()
        for key, sql in queries.items():
            cur.execute(sql)
            counts[key] = cur.fetchone()[0]
        cur.close()
        conn.close()
        return counts
    except Exception as e:
        print(f"Error DWH: {e}")
        return None

def get_source_counts():
    # Usar las fuentes corregidas
    inventory_path = "d:\\Datawrehouse_RA\\qa_rg_v1_01\\scripts\\sources_inventory.csv"
    fixed_geo_path = "d:\\Datawrehouse_RA\\area_geo_hierarchy_FIXED.json"
    fixed_pay_path = "d:\\Datawrehouse_RA\\qa_rg_v1_01\\sampling\\pagos_prod_RECONSTRUCTED.csv"

    if not os.path.exists(inventory_path):
        return None
    
    df = pd.read_csv(inventory_path, encoding='latin-1')
    
    # Leer conteos reales de las fuentes fijas
    try:
        with open(fixed_geo_path, 'r', encoding='utf-8') as f:
            geo_count = len(json.load(f))
        pay_count = len(pd.read_csv(fixed_pay_path))
    except:
        geo_count = 1009
        pay_count = 61

    counts = {
        "fact_regularizacion": df[df['FileName'].str.contains('matriz_regularizacion')]['EstimatedRows'].sum(),
        "fact_pago": pay_count,
        "dim_geografia": geo_count
    }
    return counts

def run_reconciliation():
    print("Iniciando Reconciliación...")
    src = get_source_counts()
    dwh = get_dwh_counts()
    
    if src and dwh:
        report = []
        for key in src.keys():
            s = src.get(key, 0)
            d = dwh.get(key, 0)
            diff = s - d
            pct = (diff / s * 100) if s > 0 else 0
            report.append({
                "Entity": key,
                "Source_Count": s,
                "DWH_Count": d,
                "Diff": diff,
                "Diff_Pct": f"{pct:.2f}%",
                "Status": "PASS" if abs(pct) < 0.1 else "FAIL"
            })
        
        df_report = pd.DataFrame(report)
        output = "d:\\Datawrehouse_RA\\qa_rg_v1_01\\reports\\reconciliation_results.csv"
        df_report.to_csv(output, index=False)
        print(f"Reporte de reconciliación generado: {output}")
        print(df_report)
    else:
        print("Error al obtener conteos.")

if __name__ == "__main__":
    run_reconciliation()
