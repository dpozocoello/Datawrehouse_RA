
import psycopg2

def apply_sql():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        print("--- Counting chsr_code in stg.stg_chemical_sustances_records ---")
        cur.execute("SELECT count(*) FROM stg.stg_chemical_sustances_records WHERE chsr_code IS NOT NULL;")
        print(f"chsr_code NOT NULL: {cur.fetchone()[0]}")
        cur.execute("SELECT count(*) FROM stg.stg_chemical_sustances_records WHERE chsr_code IS NULL;")
        print(f"chsr_code NULL: {cur.fetchone()[0]}")
        
        print("\n--- Sampling stg.stg_chemical_sustances_records ---")
        cur.execute("SELECT chsr_id, chsr_code, prco_id FROM stg.stg_chemical_sustances_records LIMIT 5;")
        for row in cur.fetchall():
            print(f"ID: {row[0]} | Code: {row[1]} | Prco: {row[2]}")
            
        print("--- Checking for duplicate chsd_id in stg ---")
        cur.execute("SELECT chsd_id, count(*) FROM stg.stg_chemical_substances_declaration GROUP BY 1 HAVING count(*) > 1;")
        dupes = cur.fetchall()
        print(f"Duplicate chsd_id found: {len(dupes)}")
        for d in dupes[:5]:
            print(f"  ID {d[0]}: {d[1]} times")
            
        print("\n--- Checking for duplicate chsm_id in stg ---")
        cur.execute("SELECT chsm_id, count(*) FROM stg.stg_chemical_substances_movements GROUP BY 1 HAVING count(*) > 1;")
        dupes_m = cur.fetchall()
        print(f"Duplicate chsm_id found: {len(dupes_m)}")
        
        print("\n--- Checking Geography and Logs ---")
        cur.execute("SELECT count(*) FROM dw.dim_geografia WHERE sk_geografia = 0;")
        print(f"dim_geografia Key 0: {cur.fetchone()[0]}")
        
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'dw' AND table_name = 'etl_process_log';
        """)
        print("etl_process_log columns:")
        for row in cur.fetchall():
            print(f"  - {row[0]} ({row[1]})")
            
        print("\n--- Verifying Virtual Projects in dim_proyecto ---")
        cur.execute("SELECT count(*) FROM dw.dim_proyecto WHERE sistema = 'COA_IMPORT_REG';")
        print(f"Virtual Projects (Tier 3): {cur.fetchone()[0]}")
        
        print("--- Checking Dimension Indexes ---")
        cur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname = 'dw' AND tablename = 'dim_chemical_substance' AND indexdef LIKE '%chemical_id%';")
        if cur.fetchone()[0] == 0:
            print("Creating index on dim_chemical_substance(chemical_id)...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_dim_chem_id ON dw.dim_chemical_substance(chemical_id);")
            conn.commit()
            
        cur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname = 'dw' AND tablename = 'dim_chemical_importer' AND indexdef LIKE '%importer_id%';")
        if cur.fetchone()[0] == 0:
            print("Creating index on dim_chemical_importer(importer_id)...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_dim_imp_id ON dw.dim_chemical_importer(importer_id);")
            conn.commit()
            
        print("\n--- Verifying Key 0 in Dimensions ---")
        cur.execute("SELECT count(*) FROM dw.dim_proyecto WHERE sk_proyecto = 0;")
        print(f"dim_proyecto Key 0: {cur.fetchone()[0]}")
        cur.execute("SELECT count(*) FROM dw.dim_chemical_substance WHERE chemical_key = 0;")
        print(f"dim_chemical_substance Key 0: {cur.fetchone()[0]}")
        cur.execute("SELECT count(*) FROM dw.dim_chemical_importer WHERE importer_key = 0;")
        print(f"dim_chemical_importer Key 0: {cur.fetchone()[0]}")
        cur.execute("SELECT count(*) FROM dw.dim_tiempo WHERE sk_tiempo = 0;")
        print(f"dim_tiempo Key 0: {cur.fetchone()[0]}")
        
        print("\n--- Sampling dw.dim_tiempo ---")
        cur.execute("SELECT sk_tiempo, fecha FROM dw.dim_tiempo ORDER BY sk_tiempo ASC LIMIT 5;")
        for row in cur.fetchall():
            print(f"SK: {row[0]} | Fecha: {row[1]}")
            
        print("\n--- Checking dw.dim_tiempo range ---")
        cur.execute("SELECT MIN(sk_tiempo), MAX(sk_tiempo) FROM dw.dim_tiempo;")
        min_t, max_t = cur.fetchone()
        print(f"sk_tiempo Range: {min_t} to {max_t}")
        
        print("\n--- Checking dw.dim_tiempo columns ---")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'dw' AND table_name = 'dim_tiempo';
        """)
        for row in cur.fetchall():
            print(f"Column: {row[0]} | Type: {row[1]}")
            
        print("\n--- Checking dw.fact_chemical_movement constraints ---")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'dw.fact_chemical_movement'::regclass;
        """)
        for row in cur.fetchall():
            print(f"Constraint: {row[0]} | Def: {row[1]}")
            
        print("\n--- Checking dw.fact_chemical_movement triggers ---")
        cur.execute("""
            SELECT tgname, tgenabled, pg_get_triggerdef(oid) 
            FROM pg_trigger 
            WHERE tgrelid = 'dw.fact_chemical_movement'::regclass AND NOT tgisinternal;
        """)
        for row in cur.fetchall():
            print(f"Trigger: {row[0]} | Enabled: {row[1]} | Def: {row[2]}")
            
        print("\n--- Checking dw.fact_chemical_import constraints ---")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'dw.fact_chemical_import'::regclass;
        """)
        for row in cur.fetchall():
            print(f"Constraint: {row[0]} | Def: {row[1]}")
            
        # Fetch last 5 logs
        print("\n--- Last 5 ETL Logs ---")
        cur.execute("SELECT id, process_name, start_time, status, error_message FROM dw.etl_process_log ORDER BY id DESC LIMIT 5;")
        for row in cur.fetchall():
            print(f"ID: {row[0]} | Process: {row[1]} | Start: {row[2]} | Status: {row[3]}")
            if row[4]:
                print(f"  Error: {row[4]}")
            
        print("\n--- Checking dw.dim_proyecto constraints ---")
            
        print("\n--- Checking dw.dim_proyecto columns ---")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'dw' AND table_name = 'dim_proyecto';
        """)
        for row in cur.fetchall():
            print(f"Column: {row[0]} | Type: {row[1]}")
            
        # Check if RUC or similar column exists
        cur.execute("""
            SELECT count(*) FROM pg_indexes 
            WHERE schemaname = 'dw' AND tablename = 'dim_proyecto' AND indexdef LIKE '%UNIQUE%codigo_proyecto%';
        """)
        if cur.fetchone()[0] == 0:
            print("WARNING: No unique index on dw.dim_proyecto(codigo_proyecto). Adding one...")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_dim_proj_code ON dw.dim_proyecto(codigo_proyecto);")
            conn.commit()
            
        print("\n--- Applying Refactored SP ---")
        with open('d:/Datawrehouse_RA/sp_etl_chemical_all.sql', 'r') as f:
            sql = f.read()
            cur.execute(sql)
            conn.commit()
            print("SP applied successfully.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    apply_sql()
