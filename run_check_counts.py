
import psycopg2

def check_counts():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        tables = ['dw.fact_chemical_import', 'dw.fact_chemical_movement', 'dw.fact_chemical_declaration']
        
        print("--- Final Consistency Check ---")
        for table in tables:
            print(f"\nTable: {table}")
            cur.execute(f"""
                SELECT 
                    CASE 
                        WHEN f.sk_proyecto = 0 THEN 'Orphan (SK 0)'
                        WHEN p.sistema = 'COA_IMPORT_REG' THEN 'Linked (Virtual Project)'
                        ELSE 'Linked (MAE Project)'
                    END as linkage_type,
                    count(*)
                FROM {table} f
                LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
                GROUP BY 1;
            """)
            for row in cur.fetchall():
                print(f"  {row[0]}: {row[1]}")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_counts()
