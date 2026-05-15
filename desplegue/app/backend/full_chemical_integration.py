import os
import sys
import subprocess
from sqlalchemy import create_engine, text

# Add parent dir to path for config
sys.path.insert(0, r"d:\Datawrehouse_RA\ETL_p")
from config import CONN_DWH_LOCAL

def build_uri(c):
    return f"postgresql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

def full_reset_and_load():
    engine = create_engine(build_uri(CONN_DWH_LOCAL))
    
    # 1. DROP EXISTING TABLES (Clean Slate)
    tables_to_drop = [
        "dw.fact_chemical_import",
        "dw.fact_chemical_movement",
        "dw.fact_chemical_declaration",
        "dw.dim_chemical_importer",
        "stg.stg_chemical_sustances_records",
        "stg.stg_chemical_substances_declaration",
        "stg.stg_chemical_substances_movements",
        "stg.stg_import_request",
        "stg.stg_detail_import_request",
        "stg_pesticide_project",
        "stg_products_pqa",
        "stg_detail_pesticide_project"
    ]
    
    print("--- DROP PHASE ---")
    with engine.begin() as conn:
        for t in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
                print(f"Dropped {t}")
            except Exception as e:
                print(f"Could not drop {t}: {e}")

    # 2. RUN DDL
    print("\n--- DDL PHASE ---")
    ddl_file = r"d:\Datawrehouse_RA\ddl_chemical_imports.sql"
    with open(ddl_file, "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("DDL applied successfully.")

    # 3. RUN INGESTION (PYTHON)
    print("\n--- INGESTION PHASE ---")
    scripts = [
        r"d:\Datawrehouse_RA\ETL_p\ingesta\ingesta_chemical_imports.py",
        r"d:\Datawrehouse_RA\ETL_p\ingesta\ingesta_pesticides.py"
    ]
    for s in scripts:
        print(f"Running {os.path.basename(s)}...")
        result = subprocess.run([sys.executable, s], capture_output=True, text=True)
        print(f"STDOUT:\n{result.stdout}")
        if result.returncode == 0:
            print(f"Success: {os.path.basename(s)}")
        else:
            print(f"FAILED: {os.path.basename(s)}\nSTDERR:\n{result.stderr}")

    # 4. RUN LOAD (SQL)
    print("\n--- LOAD PHASE ---")
    load_file = r"d:\Datawrehouse_RA\etl_chemical_imports_load.sql"
    with open(load_file, "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Dimensional load applied successfully.")

if __name__ == "__main__":
    try:
        full_reset_and_load()
    except Exception as e:
        print(f"GLOBAL ERROR: {e}")
