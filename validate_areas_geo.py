
import psycopg2
import json
from ETL_p.config import CONN_SUIA_ENLISY

def validate():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        # 1. Get column names specifically
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='geographical_locations' ORDER BY ordinal_position")
        geo_cols = [r[0] for r in cur.fetchall()]
        print(f"GEO_COLS: {geo_cols}")

        # 2. Get samples from geographical_locations
        cur.execute("SELECT * FROM public.geographical_locations LIMIT 10")
        geo_samples = cur.fetchall()
        print("\nGEO_SAMPLES:")
        for s in geo_samples:
            print(f"  {dict(zip(geo_cols, s))}")

        # 3. Join areas with geo
        cur.execute("""
            SELECT a.area_name, g.gelo_name, p.gelo_name as parent_name
            FROM public.areas a
            LEFT JOIN public.geographical_locations g ON a.gelo_id = g.gelo_id
            LEFT JOIN public.geographical_locations p ON g.gelo_parent_id = p.gelo_id
            WHERE a.gelo_id IS NOT NULL 
            AND a.area_status = true
            LIMIT 20
        """)
        join_res = cur.fetchall()
        print("\nJOIN_AREAS_GEO:")
        for r in join_res:
            print(f"  Area: {r[0]} | Geo: {r[1]} | Parent: {r[2]}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    validate()
