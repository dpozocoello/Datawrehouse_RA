import pandas as pd
import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179", "port": 5632, "database": "suia_enlisy", "user": "postgres", "password": "postgres"
}

def check_coa_mae_tables():
    tables = [
        'coa_mae.layers_coa',
        'coa_mae.intersections_project_licencing_coa',
        'coa_mae.project_licencing_coa',
        'coa_mae.certificate_intersection_coa'
    ]
    conn = psycopg2.connect(**CONN_PARAMS)
    for t in tables:
        try:
            pd.read_sql_query(f"SELECT * FROM {t} LIMIT 0", conn)
            print(f"[OK] {t} exists.")
        except Exception as e:
            print(f"[FAIL] {t}: {e}")
            conn.rollback() # Reset transaction after error
    conn.close()

if __name__ == "__main__":
    check_coa_mae_tables()
