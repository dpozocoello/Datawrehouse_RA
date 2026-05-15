
import psycopg2
import json
from ETL_p.config import CONN_SUIA_ENLISY

def analyze_gelo_distribution():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        # Frequency of gelo_id specifically for "Oficina Tecnica"
        cur.execute("""
            SELECT 
                g.gelo_name, 
                COUNT(a.area_id) as area_count,
                g.gelo_id
            FROM public.areas a
            JOIN public.geographical_locations g ON a.gelo_id = g.gelo_id
            WHERE a.area_name ILIKE '%OFICINA TECNICA%'
            OR a.area_name ILIKE '%DIRECCION ZONAL%'
            GROUP BY 1, 3
            ORDER BY 2 DESC
        """)
        dist = cur.fetchall()
        
        print("DISTRIBUCION DE GEO PARA OFICINAS TECNICAS/ZONALES:")
        for r in dist:
            print(f"  {r[0]} (ID:{r[2]}): {r[1]} areas")

        # Check if there are areas with gelo_id at level 3 (Canton)
        cur.execute("""
            SELECT a.area_name, g.gelo_name, p.gelo_name as parent
            FROM public.areas a
            JOIN public.geographical_locations g ON a.gelo_id = g.gelo_id
            JOIN public.geographical_locations p ON g.gelo_parent_id = p.gelo_id
            WHERE p.gelo_parent_id IS NOT NULL -- This means g is at least level 3
            LIMIT 10
        """)
        level3 = cur.fetchall()
        print("\nAREAS EN NIVEL 3 (CANTON/PARROQUIA):")
        for r in level3:
            print(f"  {r[0]} -> {r[1]} (Parent: {r[2]})")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    analyze_gelo_distribution()
