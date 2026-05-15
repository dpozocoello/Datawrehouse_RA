import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))
from config import CONN_DWH_LOCAL
from connections import get_connection

def check_sk_zeros():
    dims = ["dim_proyecto", "dim_proponente", "dim_actividad", "dim_geografia", "dim_usuario", "dim_estado", "dim_tiempo", "dim_area"]
    
    with get_connection(CONN_DWH_LOCAL) as conn:
        with conn.cursor() as cur:
            for dim in dims:
                sk_col = f"sk_{dim.replace('dim_', '')}"
                # Special case for dim_tiempo which might be sk_tiempo
                if dim == "dim_tiempo": sk_col = "sk_tiempo"
                
                try:
                    cur.execute(f"SELECT COUNT(1) FROM dw.{dim} WHERE {sk_col} = 0;")
                    count = cur.fetchone()[0]
                    print(f"{dim}: {count} records with SK=0")
                except Exception as e:
                    print(f"{dim}: Error checking - {e}")
                    conn.rollback()

if __name__ == "__main__":
    check_sk_zeros()
