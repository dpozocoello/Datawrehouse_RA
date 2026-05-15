
import psycopg2

def execute_expert_sp():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Executing dw.sp_carga_dim_area() [Expert v1.3]...")
        cur.execute("SELECT dw.sp_carga_dim_area();")
        
        # Verify Salitre fix
        print("\nVerifying Case: SALITRE...")
        cur.execute("""
            SELECT id_area, nombre_area, provincia, canton 
            FROM dw.dim_area 
            WHERE nombre_area ILIKE '%SALITRE%'
        """)
        row = cur.fetchone()
        if row:
            print(f"Area ID: {row[0]} | Name: {row[1]} | Province: {row[2]} | Canton: {row[3]}")
            if row[2] == 'GUAYAS':
                print(">>> SUCCESS: Salitre correctly mapped to GUAYAS.")
            else:
                print(f">>> FAILURE: Salitre mapped to {row[2]}.")
        else:
            print(">>> WARNING: Salitre office not found in dim_area.")

        # Verify overall normalization
        print("\nSummary of Provinces in dim_area:")
        cur.execute("SELECT provincia, COUNT(*) FROM dw.dim_area GROUP BY provincia ORDER BY 2 DESC")
        for p, count in cur.fetchall():
            print(f" - {p}: {count}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    execute_expert_sp()
