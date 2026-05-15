
import psycopg2
import pandas as pd

def audit_areas_data():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # 1. Row Counts
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM stg.suia_areas_bi")
        stg_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dw.dim_area WHERE sk_area > 0")
        dw_count = cur.fetchone()[0]
        
        print(f"--- Volume Audit ---")
        print(f"Staging (Source): {stg_count}")
        print(f"Dimension: {dw_count}")
        print(f"Difference: {stg_count - dw_count} (Possibly records with NULL gelo_id or other issues)")

        # 2. Identify Orphans (Staging not in Dim)
        query_orphans = """
        SELECT s.area_id, s.area_name, s.gelo_id
        FROM stg.suia_areas_bi s
        LEFT JOIN dw.dim_area da ON s.area_id = da.id_area
        WHERE da.id_area IS NULL;
        """
        df_orphans = pd.read_sql(query_orphans, conn)
        print(f"\n--- Orphans (Staging records not in Dimension) ---")
        print(f"Total orphans: {len(df_orphans)}")
        if not df_orphans.empty:
            print(df_orphans.head(10))

        # 3. Data Consistency Check (Common Fields)
        query_consistency = """
        SELECT s.area_id, 
               s.area_name AS stg_name, da.nombre_area AS dw_name,
               s.area_abbreviation AS stg_abbr, da.abreviatura_area AS dw_abbr,
               s.area_status AS stg_status, da.estado_area AS dw_status
        FROM stg.suia_areas_bi s
        JOIN dw.dim_area da ON s.area_id = da.id_area
        LIMIT 1000;
        """
        df_cons = pd.read_sql(query_consistency, conn)
        
        # Simple name mismatch check
        mismatched_names = df_cons[df_cons['stg_name'] != df_cons['dw_name']]
        print(f"\n--- Name Mismatches ---")
        print(f"Total mismatched names: {len(mismatched_names)}")

        # Status check logic (boolean vs string)
        # s.area_status is bool, da.estado_area is 'ACTIVO'/'INACTIVO'
        # Need to convert to same format for matching
        df_cons['stg_status_str'] = df_cons['stg_status'].apply(lambda x: 'ACTIVO' if x else 'INACTIVO')
        mismatched_status = df_cons[df_cons['stg_status_str'] != df_cons['dw_status']]
        print(f"\n--- Status Mismatches ---")
        print(f"Total mismatched states: {len(mismatched_status)}")

        # 4. Geographic Alignment Audit (Architecture Focus)
        # Join Dimension with STG Geo via STG Areas gelo_id
        query_geo_alignment = """
        SELECT da.id_area, da.nombre_area, 
               da.provincia AS dw_prov, 
               g.gelo_name AS stg_linked_name,
               g.gelo_codification_inec AS inec
        FROM dw.dim_area da
        JOIN stg.suia_areas_bi s ON da.id_area = s.area_id
        JOIN stg.geographical_locations_bi g ON s.gelo_id = g.gelo_id
        LIMIT 1000;
        """
        df_geo = pd.read_sql(query_geo_alignment, conn)
        # This checks if the resolved province/canton/parroquia in the dimension 
        # is consistent with the gelo_id linked in the source.
        # Note: dim_area.provincia might be "GUAYAS" while stg_linked_name is "SALITRE" (Canton)
        # The SP resolves hierarchy. This audit is for architectural consistency.
        
        print(f"\n--- Geographic Sample Audit (First 5) ---")
        print(df_geo.head(5))

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_areas_data()
