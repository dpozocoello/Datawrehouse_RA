
import psycopg2

def find_na_geography():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        # We need all N/A records from dim_area, and their corresponding data from STG if possible
        cur.execute("""
            SELECT da.id_area, da.nombre_area, da.abreviatura_area, da.zona, da.campus,
                   s.area_parent_id, s.gelo_id
            FROM dw.dim_area da
            LEFT JOIN stg.suia_areas_bi s ON da.id_area = s.area_id
            WHERE da.provincia = 'N/A' AND da.sk_area > 0;
        """)
        rows = cur.fetchall()
        print(f"--- AREAS WITH N/A GEOGRAPHY ({len(rows)}) ---")
        for r in rows:
            print(f"ID: {r[0]} | Name: {r[1]} | Abbr: {r[2]} | Zona: {r[3]} | Campus: {r[4]} | Parent: {r[5]} | Gelo: {r[6]}")

        # Also get a list of all Provinces from our reference table to help with matching
        cur.execute("SELECT nombre_provincia FROM ref.inec_dpa_2024;")
        provinces = [p[0] for p in cur.fetchall()]
        print(f"\n--- REFERENCE PROVINCES ---")
        print(provinces)

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_na_geography()
