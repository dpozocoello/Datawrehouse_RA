import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def check_bosque_count():
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM dw.dim_intersection WHERE dictamen_final ILIKE '%BOSQUE%'")
        count = cur.fetchone()[0]
        print(f"Total projects with BOSQUE in DWH: {count}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_bosque_count()
