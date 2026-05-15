
import pandas as pd
from sqlalchemy import create_engine

def get_provincias():
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    try:
        df = pd.read_sql("SELECT DISTINCT provincia FROM dw.dim_geografia WHERE provincia IS NOT NULL ORDER BY 1", engine)
        print("Provincias in DW:")
        print(df['provincia'].tolist())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_provincias()
