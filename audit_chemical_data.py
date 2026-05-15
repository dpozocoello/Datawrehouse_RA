import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

def audit_chemical_data():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        print("Auditing stg_fact_chemical_application quality...")
        
        queries = {
            "Total rows": "SELECT COUNT(*) FROM stg.stg_fact_chemical_application",
            "Null date_applied": "SELECT COUNT(*) FROM stg.stg_fact_chemical_application WHERE date_applied IS NULL",
            "Null chemical_id": "SELECT COUNT(*) FROM stg.stg_fact_chemical_application WHERE chemical_id IS NULL",
            "Null project_id": "SELECT COUNT(*) FROM stg.stg_fact_chemical_application WHERE project_id IS NULL",
            "Valid date (exists in dim_tiempo)": "SELECT COUNT(*) FROM stg.stg_fact_chemical_application stg JOIN dw.dim_tiempo dt ON dt.fecha = DATE(stg.date_applied)",
            "Valid project (exists in dim_proyecto)": """
                SELECT COUNT(*) 
                FROM stg.stg_fact_chemical_application stg 
                JOIN (
                    SELECT split_part(codigo_proyecto, '-', array_length(string_to_array(codigo_proyecto, '-'), 1)) as internal_id 
                    FROM dw.dim_proyecto
                ) dp ON dp.internal_id = (stg.project_id::bigint)::text
            """
        }
        
        for name, query in queries.items():
            cur.execute(query)
            print(f"{name.ljust(45)}: {cur.fetchone()[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    audit_chemical_data()
