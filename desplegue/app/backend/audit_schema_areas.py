
import psycopg2

def get_table_schema(conn, schema, table):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = '{schema}' AND table_name = '{table}'
        ORDER BY ordinal_position;
    """)
    return cur.fetchall()

def audit_areas_schema():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        stg_cols = get_table_schema(conn, 'stg', 'suia_areas_bi')
        dw_cols = get_table_schema(conn, 'dw', 'dim_area')
        
        print("--- STAGING: stg.suia_areas_bi ---")
        for col in stg_cols:
            print(f"{col[0]} ({col[1]})")
            
        print("\n--- DIMENSION: dw.dim_area ---")
        for col in dw_cols:
            print(f"{col[0]} ({col[1]})")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_areas_schema()
