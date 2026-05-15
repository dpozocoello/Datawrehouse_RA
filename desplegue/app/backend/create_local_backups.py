import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def create_backups():
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print("--- Creando Backups de Tablas Locale ---")
        
        # Backup dim_intersection
        cur.execute("CREATE TABLE IF NOT EXISTS dw.dim_intersection_bak_20260401 AS SELECT * FROM dw.dim_intersection")
        print("[OK] Backup dw.dim_intersection_bak_20260401 creado.")
        
        # Backup stg_intersection
        cur.execute("CREATE TABLE IF NOT EXISTS stg.stg_intersection_bak_20260401 AS SELECT * FROM stg.stg_intersection")
        print("[OK] Backup stg.stg_intersection_bak_20260401 creado.")
        
        conn.commit()
        conn.close()
        print("--- Backups Completados ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_backups()
