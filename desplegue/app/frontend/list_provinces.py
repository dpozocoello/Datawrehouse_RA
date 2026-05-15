from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        q = text("SELECT DISTINCT provincia FROM dw.dim_geografia ORDER BY 1")
        df = pd.read_sql(q, conn)
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
