
import psycopg2

def get_dimension_schemas():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        dims = ['dim_actividad', 'dim_proyecto', 'dim_proponente', 'dim_area']
        
        for table in dims:
            print(f"--- Schema for dw.{table} ---")
            cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = '{table}'")
            for col in cur.fetchall():
                print(f"{col[0]} ({col[1]})")
            print("-" * 30)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_dimension_schemas()
