
import sqlalchemy as sa
import pandas as pd

def check_fks():
    uri = "postgresql://postgres:postgres@172.16.0.179:5632/suia_enlisy"
    engine = sa.create_engine(uri)
    
    query = """
    SELECT
        tc.table_schema, 
        tc.table_name, 
        kcu.column_name, 
        ccu.table_schema AS foreign_table_schema,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY' 
      AND tc.table_schema = 'coa_chemical_sustances'
      AND tc.table_name = 'chemical_sustances_records';
    """
    try:
        df = pd.read_sql(query, engine)
        print("Foreign Keys for coa_chemical_sustances.chemical_sustances_records:")
        print(df)
        
        # Also check schema 'coa_mae' for project related tables
        query_mae = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'coa_mae' AND table_name LIKE '%%project%%';
        """
        df_mae = pd.read_sql(query_mae, engine)
        print("\nProject-related tables in coa_mae:")
        print(df_mae)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_fks()
