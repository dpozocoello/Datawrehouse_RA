
import psycopg2
import json
from ETL_p.config import CONN_SUIA_ENLISY

def final_validate():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        # Query areas and their full geographic path
        # Level 1: Pais (Parent IS NULL)
        # Level 2: Provincia (Parent of Level 3)
        # Level 3: Canton (Parent of Level 4)
        # Level 4: Parroquia
        
        cur.execute("""
            WITH RECURSIVE geo_path AS (
                -- Anchor: The locations directly linked to areas
                SELECT 
                    a.area_id,
                    a.area_name,
                    g.gelo_id,
                    g.gelo_name,
                    g.gelo_parent_id,
                    1 as level,
                    g.gelo_name::text as path
                FROM public.areas a
                INNER JOIN public.geographical_locations g ON a.gelo_id = g.gelo_id
                WHERE a.area_status = true
                
                UNION ALL
                
                -- Recursive step: Go up to parents
                SELECT 
                    gp.area_id,
                    gp.area_name,
                    p.gelo_id,
                    p.gelo_name,
                    p.gelo_parent_id,
                    gp.level + 1,
                    p.gelo_name || ' -> ' || gp.path
                FROM geo_path gp
                INNER JOIN public.geographical_locations p ON gp.gelo_parent_id = p.gelo_id
            )
            -- Get the longest paths (up to Pais or top level)
            SELECT DISTINCT ON (area_id)
                area_id,
                area_name,
                path,
                level
            FROM geo_path
            ORDER BY area_id, level DESC
        """)
        
        res = cur.fetchall()
        
        output_data = []
        for r in res:
            output_data.append({
                "area_id": r[0],
                "area_name": r[1],
                "geo_path": r[2],
                "depth": r[3]
            })

        output_path = r"f:\Datawrehouse_RA\area_geo_hierarchy.json"
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        print(f"SUCCESS: Hierarchy results written to {output_path}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    final_validate()
