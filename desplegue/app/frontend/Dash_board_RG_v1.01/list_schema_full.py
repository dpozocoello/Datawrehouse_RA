import pandas as pd
from sqlalchemy import create_engine, text
e = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
with e.connect() as c:
    r = c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='dw' AND table_type='BASE TABLE' ORDER BY table_name"))
    tables = [row[0] for row in r]
    print("TABLES:", tables)
    
    for table in tables:
        if table.startswith('dim_'):
            print(f"\nCOLUMNS FOR {table}:")
            r = c.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_schema='dw' AND table_name='{table}' ORDER BY ordinal_position"))
            cols = [row[0] for row in r]
            print(cols)
