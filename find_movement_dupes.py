
import psycopg2

def find_dupes():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        # 1. Create Map
        cur.execute("DROP TABLE IF EXISTS tmp_map;")
        cur.execute("""
            CREATE TEMP TABLE tmp_map AS
            SELECT r.chsr_id, 0 as sk_proyecto -- Simplified for speed
            FROM stg.stg_chemical_sustances_records r;
        """)
        
        # 2. Check for dupes in the keys
        print("--- Checking Movements Keys for Uniqueness ---")
        cur.execute("""
            SELECT s.sk_proyecto, s.chem, s.imp, s.time, s.inv, count(*)
            FROM (
                SELECT 
                    0 as sk_proyecto,
                    m.achs_id as chem,
                    d.chsr_id as imp,
                    0 as time,
                    COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id) as inv
                FROM stg.stg_chemical_substances_movements m
                JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
            ) s
            GROUP BY 1, 2, 3, 4, 5
            HAVING count(*) > 1
            LIMIT 5;
        """)
        res = cur.fetchall()
        print(f"Duplicates found: {len(res)}")
        for r in res:
            print(f"Key: {r[0..4]} | Count: {r[5]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    find_dupes()
