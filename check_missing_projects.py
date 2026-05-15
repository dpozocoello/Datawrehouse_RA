import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def check_missing_projects():
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print("--- Proyectos en stg_intersection faltantes en dim_proyecto ---")
        cur.execute("""
            SELECT count(*)
            FROM stg.stg_intersection stg
            LEFT JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
            WHERE dp.sk_proyecto IS NULL
        """)
        res = cur.fetchone()
        print(f"Total Proyectos Faltantes: {res[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_missing_projects()
