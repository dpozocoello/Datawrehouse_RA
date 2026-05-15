import pandas as pd
import psycopg2

SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}

def check_cols():
    try:
        conn = psycopg2.connect(**SUIA_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT * FROM coa_mae.project_licencing_coa LIMIT 1")
        colnames = [desc[0] for desc in cur.description]
        print(colnames)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cols()
