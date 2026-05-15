import psycopg2
import sys

def check_progress():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Check counts
        cur.execute("SELECT count(*) FROM dw.fact_pago WHERE origen = 'JBPM'")
        count_jbpm = cur.fetchone()[0]
        
        cur.execute("SELECT count(*) FROM dw.fact_pago WHERE origen = 'SUIA_RCOA'")
        count_suia = cur.fetchone()[0]
        
        cur.execute("SELECT count(*) FROM stg.online_payments_bi")
        stg_count = cur.fetchone()[0]
        
        print(f"STG Online Payments: {stg_count}")
        print(f"FACT Pago (JBPM): {count_jbpm}")
        print(f"FACT Pago (SUIA): {count_suia}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_progress()
