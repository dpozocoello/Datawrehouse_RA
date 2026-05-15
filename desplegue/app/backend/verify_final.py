import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))
from config import CONN_DWH_LOCAL
from connections import get_connection

def verify_data():
    with get_connection(CONN_DWH_LOCAL) as conn:
        with conn.cursor() as cur:
            # 1. Check dim_area
            cur.execute("SELECT COUNT(*) FROM dw.dim_area;")
            dim_count = cur.fetchone()[0]
            print(f"Total records in dim_area: {dim_count}")
            
            cur.execute("SELECT sk_area, nombre_area, zona FROM dw.dim_area LIMIT 5;")
            print("Sample records from dim_area:")
            for row in cur.fetchall():
                print(f"- {row}")
            
            # 2. Check fact_regularizacion distribution
            cur.execute("""
                SELECT 
                    da.nombre_area, 
                    COUNT(*) as total_proyectos
                FROM dw.fact_regularizacion f
                JOIN dw.dim_area da ON f.sk_area = da.sk_area
                GROUP BY da.nombre_area
                ORDER BY total_proyectos DESC
                LIMIT 10;
            """)
            print("\nProject distribution by Area (Top 10):")
            for row in cur.fetchall():
                print(f"- {row[0]}: {row[1]} projects")
                
            # 3. Check for orphans
            cur.execute("SELECT COUNT(*) FROM dw.fact_regularizacion WHERE sk_area = 0;")
            orphans = cur.fetchone()[0]
            print(f"\nProjects with 'AREA NO DEFINIDA' (SK=0): {orphans}")

            # 4. Check View
            cur.execute("SELECT oficina_tecnica, zona_administrativa FROM dw.v_dashboard_regularizacion LIMIT 5;")
            print("\nSample records from v_dashboard_regularizacion:")
            for row in cur.fetchall():
                print(f"- Area: {row[0]}, Zona: {row[1]}")

if __name__ == "__main__":
    verify_data()
