
import psycopg2
import json
from ETL_p.config import CONN_SUIA_ENLISY

def validate_to_file():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        # 1. Joins and Hierarchy
        cur.execute("""
            SELECT 
                a.area_id, 
                a.area_name, 
                g.gelo_name, 
                g.gelo_codification,
                p.gelo_name as parent_name,
                p.gelo_codification as parent_code
            FROM public.areas a
            LEFT JOIN public.geographical_locations g ON a.gelo_id = g.gelo_id
            LEFT JOIN public.geographical_locations p ON g.gelo_parent_id = p.gelo_id
            WHERE a.area_status = true
            ORDER BY a.area_name
        """)
        rows = cur.fetchall()
        
        data = []
        for r in rows:
            data.append({
                "area_id": r[0],
                "area_name": r[1],
                "geo_name": r[2],
                "geo_code": r[3],
                "parent_geo_name": r[4],
                "parent_geo_code": r[5]
            })

        output_path = r"f:\Datawrehouse_RA\geo_validation_results.json"
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"SUCCESS: Results written to {output_path}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    validate_to_file()
