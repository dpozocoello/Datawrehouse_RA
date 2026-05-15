
import psycopg2
import pandas as pd

def build_geo_reference():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # 1. Recursive query to get full hierarchy and mark levels
        query = """
        WITH RECURSIVE hierarchy AS (
            -- Level 1: ECUADOR
            SELECT gelo_id, gelo_name, gelo_parent_id, 1 as level
            FROM stg.geographical_locations_bi
            WHERE gelo_name = 'ECUADOR' AND gelo_parent_id IS NULL
            UNION ALL
            -- Levels 2, 3...
            SELECT g.gelo_id, g.gelo_name, g.gelo_parent_id, h.level + 1
            FROM stg.geographical_locations_bi g
            JOIN hierarchy h ON g.gelo_parent_id = h.gelo_id
        )
        SELECT h.gelo_id, h.gelo_name, h.level, p.gelo_name as parent_name
        FROM hierarchy h
        LEFT JOIN stg.geographical_locations_bi p ON h.gelo_parent_id = p.gelo_id;
        """
        df = pd.read_sql(query, conn)
        
        # Filter for Provinces (Level 2) and Cantons (Level 3)
        provinces = df[df['level'] == 2][['gelo_name']].rename(columns={'gelo_name': 'province'})
        cantons = df[df['level'] == 3][['gelo_name', 'parent_name']].rename(columns={'gelo_name': 'canton', 'parent_name': 'province'})
        
        print(f"Provinces found: {len(provinces)}")
        print(f"Cantons found: {len(cantons)}")
        
        # Save to CSV for the inference script
        provinces.to_csv("f:/Datawrehouse_RA/ref_provinces.csv", index=False)
        cantons.to_csv("f:/Datawrehouse_RA/ref_cantons.csv", index=False)
        
        print("\nReferences saved to f:/Datawrehouse_RA/")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_geo_reference()
