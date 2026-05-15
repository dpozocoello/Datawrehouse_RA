
import psycopg2

def get_cols():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        tables = ['stg_chemical_substances_movements', 'stg_chemical_substances_declaration']
        for t in tables:
            print(f"\n--- Columns for {t} ---")
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='stg' AND table_name='{t}';")
            for c in cur.fetchall():
                print(f"  {c[0]}")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_cols()
