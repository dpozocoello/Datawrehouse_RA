import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))

from config import CONN_DWH_LOCAL
from connections import get_connection

def test():
    try:
        with get_connection(CONN_DWH_LOCAL) as conn:
            with conn.cursor() as cur:
                print("Connected. Executing SELECT dw.sp_carga_puente_ambiental()...")
                cur.execute("SELECT dw.sp_carga_puente_ambiental();")
                conn.commit()
                print("Executed successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
