
import psycopg2

def inspect_dim_area():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        print("--- DIM_AREA (id_area=0 or sk_area=0) ---")
        cur.execute("SELECT sk_area, id_area, nombre_area FROM dw.dim_area WHERE id_area = 0 OR sk_area = 0")
        rows = cur.fetchall()
        for r in rows:
            print(r)
            
        print("\n--- DIM_AREA Total ---")
        cur.execute("SELECT COUNT(*) FROM dw.dim_area")
        print(f"Total rows: {cur.fetchone()[0]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_dim_area()
