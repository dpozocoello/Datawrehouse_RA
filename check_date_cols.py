import pandas as pd
import psycopg2

SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}

def check_cols():
    try:
        conn = psycopg2.connect(**SUIA_PARAMS)
        query = "SELECT column_name FROM information_schema.columns WHERE table_schema = 'coa_mae' AND table_name = 'project_licencing_coa' AND (column_name LIKE '%date%' OR column_name LIKE '%time%')"
        df = pd.read_sql_query(query, conn)
        with open('d:/Datawrehouse_RA/date_cols.txt', 'w') as f:
            f.write(df.to_string())
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cols()
