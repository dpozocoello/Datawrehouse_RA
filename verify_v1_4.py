
import psycopg2

def verify_v1_4():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        # 1. Apply the SP
        print("Applying SP v1.4...")
        with open(r'f:\Datawrehouse_RA\sp_expert_dim_area_v1_4.sql', 'r', encoding='utf-8') as f:
            cur.execute(f.read())
        
        # 2. Run the SP
        print("Running dw.sp_carga_dim_area()...")
        cur.execute("SELECT dw.sp_carga_dim_area();")
        
        # 3. Check Specific Cases
        print("\n--- CASE VERIFICATION ---")
        cases = ["ZONAL 2", "MILAGRO", "QUEVEDO", "BABAHOYO", "SANTA ELENA", "REGULARIZACION"]
        for case in cases:
            cur.execute(f"""
                SELECT id_area, nombre_area, provincia, canton 
                FROM dw.dim_area 
                WHERE nombre_area ILIKE '%{case}%'
                LIMIT 1;
            """)
            r = cur.fetchone()
            if r:
                print(f"Match: {r[1]} -> Prov: {r[2]}, Cant: {r[3]}")
        
        # 4. Check for remaining N/A
        cur.execute("SELECT COUNT(*) FROM dw.dim_area WHERE provincia = 'N/A' AND sk_area > 0;")
        na_count = cur.fetchone()[0]
        print(f"\nRemaining N/A Areas: {na_count}")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_v1_4()
