
import psycopg2

def find_dupes():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        print("--- Checking Movements Keys for Uniqueness ---")
        cur.execute("""
            SELECT s.chem, s.imp, s.inv, count(*)
            FROM (
                SELECT 
                    m.achs_id as chem,
                    d.chsr_id as imp,
                    COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id) as inv
                FROM stg.stg_chemical_substances_movements m
                JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
            ) s
            GROUP BY 1, 2, 3
            HAVING count(*) > 1
            LIMIT 10;
        """)
        res = cur.fetchall()
        print(f"Groups with duplicates: {len(res)}")
        for r in res:
            print(f"Chem: {r[0]} | Imp: {r[1]} | Inv: {r[2]} | Count: {r[3]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    find_dupes()
