import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def get_raw_dictamen():
    code = 'MAAE-RA-2020-363827'
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print(f"--- Raw Dictamen for {code} ---")
        cur.execute("""
            SELECT di.dictamen_final
            FROM dw.dim_intersection di
            JOIN dw.dim_proyecto dp ON di.sk_proyecto = dp.sk_proyecto
            WHERE dp.codigo_proyecto = %s
        """, (code,))
        row = cur.fetchone()
        if row:
            print(repr(row[0]))
        else:
            print("Not found")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_raw_dictamen()
