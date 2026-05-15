import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_SUIA_ENLISY

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def get_exact_cols():
    engine = create_engine(build_uri(CONN_SUIA_ENLISY))
    
    tables = [
        "coa_chemical_sustances.chemical_substances_declaration",
        "coa_chemical_sustances.chemical_substances_movements"
    ]
    
    for t in tables:
        print(f"\nTABLE: {t}")
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'coa_chemical_sustances' AND table_name = '{t.split('.')[-1]}' ORDER BY ordinal_position"
        df = pd.read_sql(query, engine)
        print(f"COLUMNS: {df['column_name'].tolist()}")

if __name__ == "__main__":
    get_exact_cols()
