from sqlalchemy import create_engine, text
import os

def run_sql_file(file_path):
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Split by semicolon but be careful with functions
        # For simplicity, we can execute the whole block if it fits
        sql = f.read()
        
    try:
        with engine.connect() as conn:
            # We will split by -- 1., -- 2. etc as markers or just use a simple regex for the parts
            # Actually, let's just execute the whole thing as one text block if possible 
            # Or split by TRUNCATE and INSERT
            
            statements = sql.split(';')
            for statement in statements:
                stmt = statement.strip()
                if stmt:
                    print(f"Executing: {stmt[:100]}...")
                    conn.execute(text(stmt))
                    conn.commit()
            print("ETL script executed successfully.")
    except Exception as e:
        print(f"Error executing script: {e}")

if __name__ == "__main__":
    run_sql_file(r'd:\DashboardRA\etl_chemical_load_v1.sql')
