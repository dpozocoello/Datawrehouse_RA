import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def check_dw():
    code = 'MAAE-RA-2020-363831'
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print(f"--- Buscando {code} en dw.dim_intersection ---")
        cur.execute("""
            SELECT di.dictamen_final, di.certificate_code, di.is_current
            FROM dw.dim_intersection di
            JOIN dw.dim_proyecto dp ON di.sk_proyecto = dp.sk_proyecto
            WHERE dp.codigo_proyecto = %s
        """, (code,))
        res = cur.fetchall()
        print(f"DW Info: {res}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dw()
