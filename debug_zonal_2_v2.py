
import psycopg2
import pandas as pd

def debug_zonal_2_v2():
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
        
        # 2. Check entries in dw.dim_area
        print("\n--- Dimension Records for 'ZONAL 2' ---")
        query_dw = """
        SELECT id_area, nombre_area, provincia, canton, parroquia 
        FROM dw.dim_area 
        WHERE nombre_area ILIKE '%ZONAL 2%';
        """
        df_dw = pd.read_sql(query_dw, conn)
        print(df_dw)

        # 3. Hierarchy Check for those specific IDs
        for idx, row in df_stg.iterrows():
            gid = row['gelo_id']
            if gid is None:
                print(f"\nArea {row['area_id']} ({row['area_name']}) has NULL gelo_id in Staging.")
                continue
                
            print(f"\nPath for Area {row['area_id']} (gelo_id {gid}):")
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
    debug_zonal_2_v2()
