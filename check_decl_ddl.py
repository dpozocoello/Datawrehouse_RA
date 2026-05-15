
import sqlalchemy as sa
import pandas as pd

def check_ddl():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    query = "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'fact_chemical_declaration';"
    df = pd.read_sql(query, engine)
    print(df)
    
    query_idx = "SELECT indexname, indexdef FROM pg_indexes WHERE schemaname = 'dw' AND tablename = 'fact_chemical_declaration';"
    df_idx = pd.read_sql(query_idx, engine)
    print("\nIndexes:")
    print(df_idx)

if __name__ == "__main__":
    check_ddl()
