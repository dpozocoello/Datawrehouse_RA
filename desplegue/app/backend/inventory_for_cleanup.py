
import psycopg2

def get_db_inventory():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        # List all tables in dw and stg schemas
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema IN ('dw', 'stg') 
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """)
        tables = cur.fetchall()
        
        print("--- DATABASE INVENTORY ---")
        for schema, table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
            count = cur.fetchone()[0]
            print(f"{schema}.{table}: {count} records")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_db_inventory()
