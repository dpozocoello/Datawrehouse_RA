
import sqlalchemy as sa
import pandas as pd

def check_all_types():
    engine = sa.create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    query = """
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'stg' 
    AND table_name IN ('stg_import_request', 'stg_detail_import_request', 'stg_chemical_substances_movements', 'stg_chemical_substances_declaration')
    AND column_name IN ('inre_authorization', 'chsd_declaration_on_time', 'chsm_entry', 'chsm_exit', 'deir_net_weight', 'deir_gross_weight');
    """
    df = pd.read_sql(query, engine)
    print(df)

if __name__ == "__main__":
    check_all_types():
