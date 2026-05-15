import psycopg2

DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def execute_load():
    try:
        conn = psycopg2.connect(**DWH_PARAMS)
        cur = conn.cursor()
        print("--- Ejecutando Carga dim_intersection ---")
        
        # 1. Marcar antiguos
        cur.execute("""
            UPDATE dw.dim_intersection di
            SET is_current = FALSE
            FROM stg.stg_intersection stg
            JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
            WHERE di.sk_proyecto = dp.sk_proyecto
              AND di.certificate_code != stg.certificate_code;
        """)
        print("[OK] Registros obsoletos marcados como is_current = FALSE")
        
        # 2. Upsert
        cur.execute("""
            INSERT INTO dw.dim_intersection (
                sk_proyecto, certificate_code, certificate_date, 
                html_location, html_layers, dictamen_final, is_current
            )
            SELECT 
                dp.sk_proyecto,
                stg.certificate_code,
                stg.certificate_date,
                stg.html_location,
                stg.html_layers,
                stg.dictamen_final,
                TRUE
            FROM stg.stg_intersection stg
            JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
            ON CONFLICT (sk_proyecto, certificate_code) DO UPDATE SET 
                certificate_date = EXCLUDED.certificate_date,
                html_location = EXCLUDED.html_location,
                html_layers = EXCLUDED.html_layers,
                dictamen_final = EXCLUDED.dictamen_final,
                is_current = TRUE;
        """)
        print(f"[OK] {cur.rowcount} registros insertados/actualizados en dim_intersection.")
        
        conn.commit()
        conn.close()
        print("--- Carga Finalizada ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    execute_load()
