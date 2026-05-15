
import sqlalchemy as sa
import pandas as pd

def check_type():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    query = "SELECT chsd_declaration_on_time FROM stg.stg_chemical_substances_declaration LIMIT 5;"
    df = pd.read_sql(query, engine)
    print(df)
    
    query_info = "SELECT data_type FROM information_schema.columns WHERE table_schema = 'stg' AND table_name = 'stg_chemical_substances_declaration' AND column_name = 'chsd_declaration_on_time';"
    df_info = pd.read_sql(query_info, engine)
    print("\nData type:")
    print(df_info)

if __name__ == "__main__":
    check_type()
