import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def discover_schemas():
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    
    query = """
        SELECT schema_name, table_name 
        FROM information_schema.tables 
        WHERE table_name LIKE '%%chemical%%' 
           OR table_name LIKE '%%import%%'
           OR table_name LIKE '%%sustanc%%'
           OR table_name LIKE '%%declaration%%'
           OR table_name LIKE '%%movement%%'
        ORDER BY 1, 2
    """
    
    print("=== SUIA PRODUCTION DISCOVERY ===")
    df = pd.read_sql(query, engine)
    print(df.to_string(index=False))
    print("================================")

if __name__ == "__main__":
    discover_schemas()
