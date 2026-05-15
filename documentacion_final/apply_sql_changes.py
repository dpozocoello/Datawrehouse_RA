import os
import sys
from sqlalchemy import create_engine, text

# Add ETL_p to path to get config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ETL_p'))
from config import CONN_DWH_LOCAL

def get_engine():
    uri = f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}"
    return create_engine(uri)

def apply_sql_file(engine, file_path):
    print(f"Applying {file_path}...")
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    with engine.connect() as conn:
        try:
            # We use text() to execute the whole block
            conn.execute(text(sql))
            conn.commit()
            print(f"Successfully applied {file_path}")
            return True
        except Exception as e:
            print(f"Error applying {file_path}: {e}")
            return False

def main():
    engine = get_engine()
    root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    
    # Order of execution is important
    files = [
        'ddl_ext_rgd_points.sql',
        'sp_etl_waste_chemical.sql'
    ]
    
    for f in files:
        path = os.path.join(root_dir, f)
        if not apply_sql_file(engine, path):
            print("Aborting due to error.")
            break
    
    print("\nProcess finished.")

if __name__ == "__main__":
    main()
