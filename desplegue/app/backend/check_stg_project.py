import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def check_stg():
    code = 'MAAE-RA-2020-363831'
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print(f"--- Buscando {code} en stg.stg_intersection ---")
        cur.execute("SELECT dictamen_final FROM stg.stg_intersection WHERE project_code = %s", (code,))
        res = cur.fetchone()
        print(f"Staging Dictamen: {res}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_stg()
