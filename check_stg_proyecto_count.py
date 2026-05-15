import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def check_stg_proyecto():
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print("--- Proyectos en stg.stg_proyecto vs dw.dim_proyecto ---")
        cur.execute("SELECT count(*) FROM stg.stg_proyecto")
        print(f"Total en STG: {cur.fetchone()[0]}")
        cur.execute("SELECT count(*) FROM dw.dim_proyecto")
        print(f"Total en DIM: {cur.fetchone()[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_stg_proyecto()
