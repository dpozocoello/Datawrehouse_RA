import psycopg2
import sys
from datetime import datetime

def check_counts():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres"
    }
    
    tablas = [
        "stg.suia_rcoa_bi",
        "stg.suia_coa_bi",
        "stg.jbpm_sector_bi",
        "stg.jbpm_4cat_bi",
        "stg.jbpm_hidro_bi",
        "stg.jbpm_snap_variables",
        "stg.online_payments_bi",
        "stg.financial_transaction_bi",
        "stg.consolidado_proyectos",
        "dw.dim_proyecto",
        "dw.fact_regularizacion",
        "dw.fact_pago"
    ]
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT now(), current_database()")
        time_db, db_name = cur.fetchone()
        print(f"DATABASE: {db_name} | DB TIME: {time_db}")
        print("-" * 60)
        print(f"{'TABLA':45s} | {'CONTEO':>10s}")
        print("-" * 60)
        for t in tablas:
            try:
                cur.execute(f"SELECT COUNT(1) FROM {t}")
                count = cur.fetchone()[0]
                print(f"{t:45s} | {count:10d}")
            except Exception as te:
                print(f"{t:45s} | ERROR: {te}")
                conn.rollback() # Recover from error to check next table
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_counts()
