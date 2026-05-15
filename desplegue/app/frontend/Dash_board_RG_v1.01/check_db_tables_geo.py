import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

try:
    print("Listing all tables in 'dw' and 'public' schemas...")
    query = """
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema IN ('dw', 'public')
    ORDER BY table_schema, table_name
    """
    df = pd.read_sql(query, engine)
    print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
