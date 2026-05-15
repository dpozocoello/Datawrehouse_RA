import psycopg2
import sys

def check_counts():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres"
    }
    
    tablas = [
        "stg.stg_waste_generator",
        "stg.stg_fact_waste_generation",
        "stg.stg_waste_type",
        "stg.stg_dangerous_waste",
        "stg.stg_dangerous_classification",
        "dw.fact_waste_generation",
        "dw.dim_waste_generator",
        "dw.dim_waste_type",
        "dw.dim_dangerous_waste",
        "dw.dim_dangerous_classification",
        "dw.dim_proyecto",
        "dw.dim_geografia",
        "dw.dim_tiempo"
    ]
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        print(f"{'TABLA':45s} | {'CONTEO':>10s}")
        print("-" * 60)
        for t in tablas:
            try:
                cur.execute(f"SELECT COUNT(1) FROM {t}")
                count = cur.fetchone()[0]
                print(f"{t:45s} | {count:10d}")
            except Exception as e:
                print(f"{t:45s} | ERROR: {e}")
                conn.rollback()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_counts()
