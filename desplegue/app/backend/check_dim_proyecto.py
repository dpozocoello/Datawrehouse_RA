import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def check_project():
    code = 'MAAE-RA-2020-363831'
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print(f"--- Buscando {code} en dw.dim_proyecto ---")
        cur.execute("SELECT sk_proyecto, codigo_proyecto FROM dw.dim_proyecto WHERE codigo_proyecto = %s", (code,))
        res = cur.fetchall()
        print(f"Project Info: {res}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_project()
