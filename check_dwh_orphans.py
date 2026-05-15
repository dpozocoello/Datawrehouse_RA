
import sqlalchemy as sa
import pandas as pd

def check_dwh_orphans():
    uri_dw = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
    engine_dw = sa.create_engine(uri_dw)
    
    try:
        query = """
        SELECT 
            (sk_proyecto = 0) as is_orphan,
            count(*) as total_records
        FROM dw.fact_chemical_import
        GROUP BY 1;
        """
        df = pd.read_sql(query, engine_dw)
        print("Chemical Import Orphans (sk_proyecto = 0):")
        print(df)
        
        query_log = "SELECT * FROM dw.etl_process_log WHERE process_name = 'Chemical ETL' ORDER BY start_time DESC LIMIT 5;"
        df_log = pd.read_sql(query_log, engine_dw)
        print("\nLast ETL Logs:")
        print(df_log)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dwh_orphans()
