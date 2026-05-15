
import psycopg2
from ETL_p.config import CONN_SUIA_ENLISY

def explore_geo():
    try:
        conn = psycopg2.connect(**CONN_SUIA_ENLISY)
        cur = conn.cursor()
        
        # 1. Columnas de areas
        print("--- COLUMNAS DE public.areas ---")
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='areas' ORDER BY 1")
        cols = cur.fetchall()
        for c in cols:
            print(f"  {c[0]} ({c[1]})")

        # 2. Tablas que contengan 'geog' o 'gelo'
        print("\n--- TABLAS GEOGRAFICAS ---")
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name ILIKE '%geog%' OR table_name ILIKE '%gelo%'")
        tabs = cur.fetchall()
        for t in tabs:
            print(f"  {t[0]}.{t[1]}")

        # 3. Si existe geographic_location, ver su data
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name='geographic_location'")
        if cur.fetchone():
            print("\n--- COLUMNAS DE public.geographic_location ---")
            cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='geographic_location' ORDER BY 1")
            for c in cur.fetchall():
                print(f"  {c[0]} ({c[1]})")
            
            print("\n--- MUESTRA DE geographic_location ---")
            cur.execute("SELECT * FROM public.geographic_location LIMIT 5")
            for r in cur.fetchall():
                print(f"  {r}")

        # 4. Ver si gelo_id en areas tiene valores y a qué tipo de nivel corresponden
        print("\n--- VALORES DE gelo_id EN areas ---")
        cur.execute("SELECT gelo_id, COUNT(*) FROM public.areas GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
        for r in cur.fetchall():
            print(f"  gelo_id: {r[0]}, count: {r[1]}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_geo()
