
import psycopg2
import pandas as pd

def inec_hierarchy_validation():
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
    
    # Get nodes from level 2 (Province) and level 3 (Canton)
    query = """
    WITH RECURSIVE geo_tree AS (
        SELECT gelo_id, gelo_name, gelo_parent_id, gelo_codification_inec, 1 as level
        FROM stg.geographical_locations_bi
        WHERE gelo_name = 'ECUADOR'
        UNION ALL
        SELECT g.gelo_id, g.gelo_name, g.gelo_parent_id, g.gelo_codification_inec, gt.level + 1
        FROM stg.geographical_locations_bi g
        JOIN geo_tree gt ON g.gelo_parent_id = gt.gelo_id
    )
    SELECT gt.gelo_id, gt.gelo_name, gt.gelo_codification_inec, gt.level, 
           parent.gelo_name as parent_name, parent.gelo_codification_inec as parent_inec
    FROM geo_tree gt
    LEFT JOIN geo_tree parent ON gt.gelo_parent_id = parent.gelo_id;
    """
    
    df = pd.read_sql(query, conn)
    
    # Validation: First two digits of Canton (level 3) must match Province (level 2) INEC
    level3 = df[df['level'] == 3].copy()
    level3['parent_prefix'] = level3['gelo_codification_inec'].str[:2]
    
    # Detect mismatches
    # parent_inec is the province's 2-digit code
    mismatches = level3[(level3['parent_prefix'] != level3['parent_inec']) & (level3['parent_inec'].notna())]
    
    print(f"Total Cantons analyzed: {len(level3)}")
    print(f"Mismatches found (Canton prefix != Parent Province INEC): {len(mismatches)}")
    
    if len(mismatches) > 0:
        print("\n--- Detected Mismatches (Potential Integrity Failures) ---")
        print(mismatches[['gelo_name', 'gelo_codification_inec', 'parent_name', 'parent_inec']].head(10))
    else:
        print("\nAll Cantons correctly belong to their Provinces according to INEC codes.")

    conn.close()

if __name__ == "__main__":
    inec_hierarchy_validation()
