
import psycopg2

def dynamic_cleanup():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        cur = conn.cursor()
        
        # 1. Get all tables in dw and stg
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema IN ('dw', 'stg') 
            AND table_type = 'BASE TABLE'
            AND table_name NOT IN ('dim_tiempo'); -- Skip static dim_tiempo
        """)
        tables = cur.fetchall()
        
        # 2. Build truncate statements
        # We need to truncate fact tables first or use CASCADE
        fact_tables = []
        dim_tables = []
        stg_tables = []
        
        for schema, table in tables:
            full_name = f"{schema}.{table}"
            if schema == 'stg':
                stg_tables.append(full_name)
            elif 'fact_' in table:
                fact_tables.append(full_name)
            else:
                dim_tables.append(full_name)
                
        # Order: Facts, then Dims/Stg
        all_to_truncate = fact_tables + dim_tables + stg_tables
        
        print("Starting Dynamic Cleanup...")
        for table in all_to_truncate:
            try:
                print(f"Truncating {table}...")
                cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
            except Exception as te:
                print(f"Skipping {table}: {te}")
                conn.rollback()
                continue
        
        # 3. Reset common sequences
        sequences = [
            'dw.dim_proyecto_sk_proyecto_seq',
            'dw.dim_proponente_sk_proponente_seq',
            'dw.dim_area_sk_area_seq',
            'dw.dim_pago_sk_pago_seq',
            'dw.dim_actividad_sk_actividad_seq'
        ]
        for seq in sequences:
            try:
                cur.execute(f"ALTER SEQUENCE IF EXISTS {seq} RESTART WITH 1;")
            except:
                pass
                
        conn.commit()
        print("Cleanup complete.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dynamic_cleanup()
