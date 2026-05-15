import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"  # Change if needed
}

def check_columns():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        table_name = "stg.stg_waste_type"
        print(f"Checking columns for {table_name}...")
        
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'stg' 
              AND table_name = 'stg_waste_type'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        if not columns:
            print(f"Table {table_name} not found or has no columns.")
        else:
            for col, dtype in columns:
                print(f" - {col}: {dtype}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    check_columns()
