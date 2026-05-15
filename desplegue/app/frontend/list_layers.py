from sqlalchemy import create_engine, text
import pandas as pd

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM dw.dim_capa_ambiental ORDER BY sk_capa", conn)
        print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
