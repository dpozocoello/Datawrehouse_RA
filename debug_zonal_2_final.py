
import psycopg2

def debug_zonal_2_final():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        # 1. Search in Staging
        cur.execute("SELECT area_id, area_name, gelo_id, zone_id FROM stg.suia_areas_bi WHERE area_name ILIKE '%ZONAL 2%'")
        rows_stg = cur.fetchall()
        print(f"--- STAGING RECORDS ({len(rows_stg)}) ---")
        for r in rows_stg:
            print(f"ID: {r[0]} | Name: {r[1]} | GeloID: {r[2]} | Zone: {r[3]}")

        # 2. Search in Dimension
        cur.execute("SELECT id_area, nombre_area, provincia, canton, parroquia FROM dw.dim_area WHERE nombre_area ILIKE '%ZONAL 2%'")
        rows_dw = cur.fetchall()
        print(f"\n--- DIMENSION RECORDS ({len(rows_dw)}) ---")
        for r in rows_dw:
            print(f"ID: {r[0]} | Name: {r[1]} | Prov: {r[2]} | Cant: {r[3]} | Parr: {r[4]}")

        # 3. If GeloID exists but no Prov, trace the path
        # Assuming we might find at least one. If not, analyze why.
        gelos_to_trace = list(set([r[2] for r in rows_stg if r[2] is not None]))
        for gid in gelos_to_trace:
            print(f"\n--- TRACING PATH FOR GeloID: {gid} ---")
            cur.execute(f"""
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
            """)
            path = cur.fetchall()
            for p in path:
                print(f"Lvl {p[4]}: {p[1]} (ID: {p[0]}, Parent: {p[2]}, INEC: {p[3]})")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_zonal_2_final()
