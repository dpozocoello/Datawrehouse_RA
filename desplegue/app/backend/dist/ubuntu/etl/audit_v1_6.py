import pandas as pd
from sqlalchemy import create_engine
from config import CONN_DWH_LOCAL

def audit():
    uri = f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}"
    engine = create_engine(uri)
    
    queries = {
        "Generadores (Total)": "SELECT count(*) FROM dw.dim_waste_generator",
        "Generadores (con RUC)": "SELECT count(*) FROM dw.dim_waste_generator WHERE ruc_generator IS NOT NULL",
        "Trazabilidad Pagos (Filas)": "SELECT count(*) FROM dw.fact_payment_traceability",
        "Trazabilidad Pagos (Delta != 0)": "SELECT count(*) FROM dw.fact_payment_traceability WHERE delta_value != 0",
        "Procesos BPM (RGD)": "SELECT count(*) FROM dw.dim_process_flow WHERE process_type = 'RGD'"
    }
    
    print("/n" + "="*50)
    print("REPORTE DE AUDITORÍA DATA WAREHOUSE v1.6")
    print("="*50)
    
    for name, q in queries.items():
        res = pd.read_sql(q, engine).iloc[0, 0]
        print(f"{name:30} : {res:>10,}")
    
    print("="*50 + "/n")

if __name__ == "__main__":
    audit()
