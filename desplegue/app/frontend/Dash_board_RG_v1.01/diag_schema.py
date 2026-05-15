import pandas as pd
from sqlalchemy import create_engine, text
e = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
with e.connect() as c:
    r = c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='dw' AND table_name='users' ORDER BY ordinal_position"))
    cols = [row[0] for row in r]
    print("COLUMNS:", cols)
    
    # Check if is_active column exists
    print("HAS is_active:", 'is_active' in cols)
