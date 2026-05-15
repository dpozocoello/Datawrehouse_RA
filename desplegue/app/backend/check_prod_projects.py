import psycopg2

SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}

def check_prod_projects():
    try:
        conn = psycopg2.connect(**SUIA_PARAMS)
        cur = conn.cursor()
        print("--- Proyectos en coa_mae.project_licencing_coa ---")
        cur.execute("SELECT count(*) FROM coa_mae.project_licencing_coa")
        print(f"Total en Producción: {cur.fetchone()[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_prod_projects()
