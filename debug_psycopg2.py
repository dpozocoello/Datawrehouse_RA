import pandas as pd
import psycopg2

CONN_PARAMS = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

def run_direct_audit():
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        print("--- Conexión Psycopg2 OK ---")
        
        query = """
            SELECT 
                plc.prco_cua as project_code,
                lc.laye_id,
                lc.laye_name
            FROM coa_mae.intersections_project_licencing_coa iplc
            JOIN coa_mae.project_licencing_coa plc ON iplc.prco_id = plc.prco_id
            JOIN coa_mae.layers_coa lc ON iplc.laye_id = lc.laye_id
            WHERE iplc.inpr_status = TRUE
            LIMIT 10
        """
        df = pd.read_sql_query(query, conn)
        print(df)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_direct_audit()
