import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def run_step_by_step():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    
    with open(r"d:\Datawrehouse_RA\etl_chemical_imports_load.sql", "r", encoding="utf-8") as f:
        full_sql = f.read()
    
    # Split by semicolon and empty lines (crude split)
    # Better: split by comments or known sections
    sections = full_sql.split("-- ------------------------------------------------------------------------------")
    
    for i, section in enumerate(sections):
        if i == 0: continue # Header
        print(f"\n--- EXECUTING SECTION {i} ---")
        try:
            with engine.begin() as conn:
                conn.execute(text(section))
            print(f"Section {i} SUCCESS.")
        except Exception as e:
            print(f"Section {i} FAILED: {e}")

if __name__ == "__main__":
    run_step_by_step()
