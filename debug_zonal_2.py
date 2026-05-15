
import psycopg2
import pandas as pd

def debug_zonal_2():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # 1. Check entries in stg.suia_areas_bi
        print("--- Staging Records for 'ZONAL 2' ---")
        query_stg = """
        SELECT area_id, area_name, gelo_id, zone_id 
        FROM stg.suia_areas_bi 
        WHERE area_name ILIKE '%ZONAL 2%';
        """
        df_stg = pd.read_sql(query_stg, conn)
        print(df_stg)

        if df_stg.empty:
            print("No records found in Staging for 'ZONAL 2'.")
            return

        # 2. Check entries in dw.dim_area
        print("\n--- Dimension Records for 'ZONAL 2' ---")
        query_dw = """
        SELECT id_area, nombre_area, provincia, canton, parroquia 
        FROM dw.dim_area 
        WHERE nombre_area ILIKE '%ZONAL 2%';
        """
        df_dw = pd.read_sql(query_dw, conn)
        print(df_dw)

        # 3. Analyze Geography Path for each unique gelo_id found
        unique_gelos = df_stg['gelo_id'].unique()
        print(f"\n--- Geographic Hierarchy for gelo_ids: {unique_gelos} ---")
        
        for gid in unique_gelos:
            if gid is None: continue
            print(f"\nPath for gelo_id {gid}:")
            query_path = f"""
            WITH RECURSIVE geo_path AS (
                SELECT gelo_id, gelo_name, gelo_parent_id, gelo_codification_inec, 1 as level
                FROM stg.geographical_locations_bi
                WHERE gelo_id = {gid}
                UNION ALL
                SELECT g.gelo_id, g.gelo_name, g.gelo_parent_id, g.gelo_codification_inec, gp.level + 1
                FROM stg.geographical_locations_bi g
                JOIN geo_path gp ON g.gelo_id = gp.gelo_parent_id
            )
            SELECT * FROM geo_path;
            """
            df_path = pd.read_sql(query_path, conn)
            print(df_path)

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_zonal_2()
