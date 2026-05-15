import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def audit_schema():
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    query = """
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'coa_chemical_sustances' 
        ORDER BY table_name, ordinal_position
    """
    df = pd.read_sql(query, engine)
    print(df.to_string(index=False))

if __name__ == "__main__":
    audit_schema()
