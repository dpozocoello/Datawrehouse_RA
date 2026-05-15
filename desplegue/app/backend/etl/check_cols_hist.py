import pandas as pd
from sqlalchemy import create_engine
import sys

sys.path.append(r'F:\Datawrehouse_RA\ETL_p')
from config import CONN_JBPM

def test():
    e_jbpm = create_engine(f"postgresql://{CONN_JBPM['user']}:{CONN_JBPM['password']}@{CONN_JBPM['host']}:{CONN_JBPM['port']}/{CONN_JBPM['database']}")
    
    try:
        df_hist = pd.read_sql("SELECT * FROM online_payment.online_payments_historical LIMIT 1", e_jbpm)
        print("HISTORICAL Cols:", df_hist.columns.tolist())
    except Exception as e:
        print("Error historical:", e)
        
if __name__ == '__main__':
    test()
