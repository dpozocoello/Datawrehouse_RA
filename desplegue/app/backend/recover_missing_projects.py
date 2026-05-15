import pandas as pd
import psycopg2

# Conexiones
SUIA_PARAMS = {"host":"172.16.0.179", "port":5632, "database":"suia_enlisy", "user":"postgres", "password":"postgres"}
DWH_PARAMS = {"host":"localhost", "port":5432, "database":"dw_reg_v1", "user":"postgres", "password":"postgres"}

def recover_missing_projects():
    try:
        # 1. Identificar proyectos faltantes
        conn_dwh = psycopg2.connect(**DWH_PARAMS)
        query_missing = """
            SELECT DISTINCT stg.project_code
            FROM stg.stg_intersection stg
            LEFT JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
            WHERE dp.sk_proyecto IS NULL
        """
        df_missing = pd.read_sql_query(query_missing, conn_dwh)
        conn_dwh.close()
        
        missing_codes = df_missing['project_code'].tolist()
        print(f"--- Proyectos a recuperar: {len(missing_codes)} ---")
        
        if not missing_codes:
            print("No hay proyectos faltantes.")
            return

        # 2. Extraer de producción (sólo columnas existentes en DWH)
        conn_suia = psycopg2.connect(**SUIA_PARAMS)
        df_recovered_list = []
        batch_size = 5000
        for i in range(0, len(missing_codes), batch_size):
            batch = missing_codes[i:i+batch_size]
            query_prod = """
                SELECT 
                    prco_cua as codigo_proyecto, 
                    prco_name as nombre_proyecto, 
                    prco_description as resumen_proyecto,
                    'SUIA-INTERSECTION-RECOVERY' as sistema 
                FROM coa_mae.project_licencing_coa 
                WHERE prco_cua IN %s
            """
            df_temp = pd.read_sql_query(query_prod, conn_suia, params=(tuple(batch),))
            df_recovered_list.append(df_temp)
        df_recovered = pd.concat(df_recovered_list)
        conn_suia.close()
        print(f"--- Datos recuperados de producción: {len(df_recovered)} ---")
        
        # 3. Insertar en dw.dim_proyecto
        conn_dwh = psycopg2.connect(**DWH_PARAMS)
        cur = conn_dwh.cursor()
        
        insert_query = """
            INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto, resumen_proyecto, sistema) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT (codigo_proyecto) DO NOTHING
        """
        data = [(row['codigo_proyecto'], row['nombre_proyecto'], row['resumen_proyecto'], row['sistema']) for _, row in df_recovered.iterrows()]
        
        from psycopg2.extras import execute_batch
        execute_batch(cur, insert_query, data)
        
        conn_dwh.commit()
        print(f"[OK] {len(data)} proyectos insertados/procesados en dw.dim_proyecto.")
        conn_dwh.close()
        
        print("--- Proceso de Recuperación de Proyectos Finalizado ---")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    recover_missing_projects()
