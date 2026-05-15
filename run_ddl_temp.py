import os
import sys
from sqlalchemy import create_engine, text

# Add parent dir to path for config
sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def run_ddl(file_path):
    print(f"Connecting to {CONN_DWH_LOCAL['database']} on {CONN_DWH_LOCAL['host']}...")
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split by semicolon to execute block by block if needed, 
    # but sqlalchemy can often handle the whole thing if it's just DDL
    with engine.begin() as conn:
        print(f"Executing DDL from {file_path}...")
        conn.execute(text(sql))
    print("DDL executed successfully.")

if __name__ == "__main__":
    ddl_file = r"d:\Datawrehouse_RA\ddl_chemical_imports.sql"
    try:
        run_ddl(ddl_file)
    except Exception as e:
        print(f"Error: {e}")
