import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def check_dw_dictamen():
    code = 'MAAE-RA-2020-363827'
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print(f"--- Dictamen en DW para {code} ---")
        cur.execute("""
            SELECT di.dictamen_final
            FROM dw.dim_intersection di
            JOIN dw.dim_proyecto dp ON di.sk_proyecto = dp.sk_proyecto
            WHERE dp.codigo_proyecto = %s
        """, (code,))
        res = cur.fetchone()
        print(f"Dictamen: {res}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dw_dictamen()
