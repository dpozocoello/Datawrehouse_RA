import psycopg2

CONN_DWH_LOCAL = {
    "host": "localhost",
    "port": 5432,
    "database": "dw_reg_v1",
    "user": "postgres",
    "password": "postgres"
}

tablas_stg = [
    "stg.stg_waste_generator",
    "stg.stg_waste_type",
    "stg.stg_dangerous_waste",
    "stg.stg_dangerous_classification",
    "stg.stg_chemical_substance",
    "stg.stg_chemical_storage",
    "stg.stg_fact_waste_generation",
    "stg.stg_fact_chemical_application"
]

tablas_dw = [
    "dw.dim_waste_generator",
    "dw.dim_waste_type",
    "dw.dim_dangerous_waste",
    "dw.dim_dangerous_classification",
    "dw.dim_chemical_substance",
    "dw.dim_chemical_storage",
    "dw.fact_waste_generation",
    "dw.fact_chemical_application",
    "dw.fact_project_environmental_impact"
]

def print_counts():
    try:
        conn = psycopg2.connect(**CONN_DWH_LOCAL)
        cur = conn.cursor()
        
        print("====== CONTEOS STG ======")
        for t in tablas_stg:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                print(f"{t.ljust(40)}: {cur.fetchone()[0]} filas")
            except Exception as e:
                print(f"{t.ljust(40)}: ERROR - {e}")
                conn.rollback()

        print("\n====== CONTEOS DW ======")
        for t in tablas_dw:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                print(f"{t.ljust(40)}: {cur.fetchone()[0]} filas")
            except Exception as e:
                print(f"{t.ljust(40)}: ERROR - {e}")
                conn.rollback()
                
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    print_counts()
