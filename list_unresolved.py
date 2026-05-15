
import psycopg2

def list_unresolved():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        cur.execute("""
            SELECT da.id_area, da.nombre_area, s.area_campus, s.area_abbreviation, s.zone_id
            FROM dw.dim_area da 
            JOIN stg.suia_areas_bi s ON da.id_area = s.area_id 
            WHERE da.provincia = 'N/A' AND da.sk_area > 0
        """)
        rows = cur.fetchall()
        print(f"--- UNRESOLVED AREAS ({len(rows)}) ---")
        for r in rows:
            print(f"ID: {r[0]} | Name: {r[1]} | Campus: {r[2]} | Abbr: {r[3]} | Zone: {r[4]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_unresolved()
