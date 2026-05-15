from sqlalchemy import create_engine, text
import pandas as pd
import sys

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Table Search ---")
        query = text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%capa%' OR table_name LIKE '%ambiental%'")
        result = conn.execute(query)
        for row in result:
            print(f"Schema: {row[0]}, Table: {row[1]}")
        
        print("\n--- Columns in fact_regularizacion ---")
        columns = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'fact_regularizacion'"))
        for col in columns:
            print(f"Col: {col[0]}, Type: {col[1]}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
