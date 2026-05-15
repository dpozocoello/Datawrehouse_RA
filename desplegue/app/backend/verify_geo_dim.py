
import psycopg2
from ETL_p.config import CONN_DWH_LOCAL

def verify_dim_area():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        print("--- DIM_AREA GEOGRAPHIC DATA ---")
        cur.execute("""
            SELECT nombre_area, provincia, canton, parroquia 
            FROM dw.dim_area 
            WHERE provincia != 'N/A' 
            ORDER BY provincia, canton, parroquia
            LIMIT 50
        """)
        rows = cur.fetchall()
        for r in rows:
            print(f"Area: {r[0]:<50} | Prov: {r[1]:<15} | Cant: {r[2]:<15} | Parr: {r[3]:<15}")
            
        cur.execute("SELECT COUNT(*) FROM dw.dim_area WHERE provincia != 'N/A'")
        count = cur.fetchone()[0]
        print(f"\nTotal areas con geografía: {count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_dim_area()
