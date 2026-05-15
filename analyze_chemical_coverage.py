import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def analyze_chemical_coverage():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        print("Analyzing Chemical Project Mapping Coverage...")
        
        # 1. Unique project IDs in staging
        cur.execute("SELECT COUNT(DISTINCT (project_id::bigint)::text) FROM stg.stg_fact_chemical_application WHERE project_id IS NOT NULL")
        unique_stg = cur.fetchone()[0]
        print(f"Unique project IDs in chemical staging: {unique_stg}")
        
        # 2. Sample IDs from staging
        cur.execute("SELECT DISTINCT (project_id::bigint)::text FROM stg.stg_fact_chemical_application WHERE project_id IS NOT NULL LIMIT 10")
        samples = [c[0] for c in cur.fetchall()]
        print(f"Sample IDs: {samples}")
        
        # 3. Matches in dim_proyecto
        cur.execute("""
            SELECT COUNT(DISTINCT stg.project_id) 
            FROM stg.stg_fact_chemical_application stg 
            JOIN (
                SELECT split_part(codigo_proyecto, '-', array_length(string_to_array(codigo_proyecto, '-'), 1)) as internal_id 
                FROM dw.dim_proyecto
            ) dp ON dp.internal_id = (stg.project_id::bigint)::text
        """)
        matches = cur.fetchone()[0]
        print(f"Project IDs with matches in dim_proyecto: {matches}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    analyze_chemical_coverage()
