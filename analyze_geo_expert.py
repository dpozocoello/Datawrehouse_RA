
import psycopg2
import pandas as pd
import sys

def analyze_geo_expert():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # 1. Catalog Level Analysis
        query_cat = "SELECT * FROM stg.geographical_locations_bi"
        df_cat = pd.read_sql(query_cat, conn)
        
        # 2. Hierarchy Resolution (Recursive)
        query_tree = """
        WITH RECURSIVE geo_tree AS (
            SELECT gelo_id, gelo_name, gelo_parent_id, gelo_codification_inec, 1 as level
            FROM stg.geographical_locations_bi
            WHERE gelo_name = 'ECUADOR'
            UNION ALL
            SELECT g.gelo_id, g.gelo_name, g.gelo_parent_id, g.gelo_codification_inec, gt.level + 1
            FROM stg.geographical_locations_bi g
            JOIN geo_tree gt ON g.gelo_parent_id = gt.gelo_id
        )
        SELECT * FROM geo_tree;
        """
        df_tree = pd.read_sql(query_tree, conn)
        
        print(f"Total nodes in hierarchy: {len(df_tree)}")
        print("Levels distribution:")
        print(df_tree['level'].value_counts().sort_index())
        
        # 3. Area Mapping Check
        query_areas = """
        SELECT a.area_id, a.area_name, a.gelo_id, 
               da.provincia, da.canton, da.parroquia
        FROM stg.suia_areas_bi a
        LEFT JOIN dw.dim_area da ON a.area_id = da.id_area
        WHERE a.area_id IS NOT NULL;
        """
        df_areas = pd.read_sql(query_areas, conn)
        
        # 4. Expert Observation: Check for anomalies
        # Offices that are at Level 2 (Province) but have Canton or Parroquia name in area_name
        # (This suggests a possible mapping error or a very specific local office)
        
        # Summary of Areas by Province
        print("\nSummary by Province (dw.dim_area):")
        print(df_areas['provincia'].value_counts())
        
        # Check for nulls in geography
        null_geo = df_areas[df_areas['provincia'].isna() | (df_areas['provincia'] == '')]
        print(f"\nAreas without resolved geography: {len(null_geo)}")
        if len(null_geo) > 0:
            print(null_geo[['area_id', 'area_name']].head(5))

        # Check INEC code lengths for consistency
        # level 2 = 2 chars
        # level 3 = 4 chars
        # level 4 = 6 chars
        print("\nINEC Code Length Consistency per Level:")
        df_tree['inec_len'] = df_tree['gelo_codification_inec'].str.len()
        print(df_tree.groupby('level')['inec_len'].value_counts().sort_index())

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_geo_expert()
