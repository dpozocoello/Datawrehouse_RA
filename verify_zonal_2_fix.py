
import psycopg2

def verify_zonal_2_fix():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        # 1. Update the SP in the database
        print("Applying SP v1.3.1...")
        with open(r'f:\Datawrehouse_RA\sp_expert_dim_area_v1_3_1.sql', 'r', encoding='utf-8') as f:
            cur.execute(f.read())
        
        # 2. Execute the SP
        print("Executing dw.sp_carga_dim_area()...")
        cur.execute("SELECT dw.sp_carga_dim_area();")
        
        # 3. Verify Zonal 2
        print("\n--- Verification: 'DIRECCIÓN ZONAL 2' ---")
        cur.execute("""
            SELECT id_area, nombre_area, provincia, canton, parroquia 
            FROM dw.dim_area 
            WHERE nombre_area ILIKE '%ZONAL 2%';
        """)
        row = cur.fetchone()
        if row:
            print(f"ID: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Provincia: {row[2]} (Expected: NAPO)")
            print(f"Canton: {row[3]} (Expected: TENA)")
            print(f"Parroquia: {row[4]}")
        else:
            print("Record not found in Dimension.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_zonal_2_fix()
