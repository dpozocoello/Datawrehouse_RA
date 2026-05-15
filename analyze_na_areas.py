
import psycopg2

def analyze_na_areas():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        # Get areas with N/A geography and more fields for context
        cur.execute("""
            SELECT s.area_id, s.area_name, s.area_campus, s.area_abbreviation, s.zone_id, s.area_parent_id,
                   da.nombre_area as dw_name
            FROM stg.suia_areas_bi s
            JOIN dw.dim_area da ON s.area_id = da.id_area
            WHERE da.provincia = 'N/A' AND da.sk_area > 0;
        """)
        rows = cur.fetchall()
        
        print(f"Total N/A Areas: {len(rows)}\n")
        print(f"{'ID':<6} | {'Name':<40} | {'Campus':<25} | {'Zone':<5} | {'Parent':<6}")
        print("-" * 100)
        for r in rows:
            print(f"{r[0]:<6} | {r[1][:40]:<40} | {str(r[2])[:25]:<25} | {str(r[4]):<5} | {str(r[5]):<6}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_na_areas()
