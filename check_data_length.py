import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "ETL_p"))
from config import CONN_DWH_LOCAL
from connections import get_connection

def check_lengths():
    query = "SELECT MAX(LENGTH(intersecta_con)) FROM stg.consolidado_proyectos;"
    query2 = "SELECT intersecta_con FROM stg.consolidado_proyectos WHERE LENGTH(intersecta_con) > 100 LIMIT 5;"
    
    with get_connection(CONN_DWH_LOCAL) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            max_len = cur.fetchone()[0]
            print(f"Max length of intersecta_con: {max_len}")
            
            cur.execute(query2)
            examples = cur.fetchall()
            if examples:
                print("Examples > 100:")
                for ex in examples:
                    print(f"- {ex[0][:150]}...")

if __name__ == "__main__":
    check_lengths()
