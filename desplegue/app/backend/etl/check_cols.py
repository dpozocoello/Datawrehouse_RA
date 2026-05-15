import pandas as pd
from sqlalchemy import create_engine
import sys

sys.path.append(r'F:\Datawrehouse_RA\ETL_p')
from config import CONN_SUIA_ENLISY, CONN_JBPM

def test():
    e_suia = create_engine(f"postgresql://{CONN_SUIA_ENLISY['user']}:{CONN_SUIA_ENLISY['password']}@{CONN_SUIA_ENLISY['host']}:{CONN_SUIA_ENLISY['port']}/{CONN_SUIA_ENLISY['database']}")
    e_jbpm = create_engine(f"postgresql://{CONN_JBPM['user']}:{CONN_JBPM['password']}@{CONN_JBPM['host']}:{CONN_JBPM['port']}/{CONN_JBPM['database']}")
    
    try:
        df_cruze = pd.read_sql("SELECT * FROM public.cruze LIMIT 1", e_jbpm)
        print("CRUZE Cols:", df_cruze.columns.tolist())
    except Exception as e:
        print("Error cruze:", e)
        
    try:
        df_tmp = pd.read_sql("SELECT * FROM public.tmp_accion_emision LIMIT 1", e_suia)
        print("TMP_ACCION Cols:", df_tmp.columns.tolist())
    except Exception as e:
        print("Error tmp:", e)
        
if __name__ == '__main__':
    test()
