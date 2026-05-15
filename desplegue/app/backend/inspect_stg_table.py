import pandas as pd
from sqlalchemy import create_engine
import sys
sys.path.append('D:/Datawrehouse_RA')
from ETL_p.config import CONN_DWH_LOCAL

def main():
    uri = f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}"
    engine = create_engine(uri)
    
    query = """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'stg' 
    AND table_name = 'online_payments_historical_bi' 
    ORDER BY ordinal_position
    """
    
    df = pd.read_sql(query, engine)
    print("--- COLUMNS IN stg.online_payments_historical_bi ---")
    print(df.to_string())

if __name__ == "__main__":
    main()
