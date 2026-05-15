import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))

from config import CONN_DWH_LOCAL
from connections import get_connection

def check():
    try:
        with get_connection(CONN_DWH_LOCAL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT routine_schema, routine_name 
                    FROM information_schema.routines 
                    WHERE routine_name LIKE 'sp_carga_puente%' 
                       OR routine_name LIKE 'sp_orquestar%';
                """)
                rows = cur.fetchall()
                print("Functions found:")
                for r in rows:
                    print(f" - {r[0]}.{r[1]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
