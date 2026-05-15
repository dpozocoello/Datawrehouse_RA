import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY

def find_string_in_record():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        target_id = 542234
        search_string = "INTERSECA" # Broad search
        
        print(f"Searching for '{search_string}' in all columns for Project {target_id}...")
        
        cur.execute("SELECT * FROM coa_mae.certificate_intersection_coa WHERE prco_id = %s", (target_id,))
        row = cur.fetchone()
        
        if not row:
            print("Row not found.")
            return
            
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='coa_mae' AND table_name='certificate_intersection_coa'")
        cols = [r[0] for r in cur.fetchall()]
        
        found = False
        for i, val in enumerate(row):
            col_name = cols[i]
            val_str = str(val)
            if search_string in val_str.upper():
                print(f"FOUND IN [{col_name}]:")
                print(f"{val_str}")
                print("-" * 20)
                found = True
        
        if not found:
            print("String not found in any column of this table.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_string_in_record()
