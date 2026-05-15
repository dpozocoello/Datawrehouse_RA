
import sqlalchemy as sa
import pandas as pd

def check_stg_counts():
    uri_dw = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
    engine_dw = sa.create_engine(uri_dw)
    
    tables = [
        "stg.stg_import_request",
        "stg.stg_detail_import_request",
        "stg.stg_chemical_sustances_records",
        "stg.stg_project_mapping",
        "stg.stg_chemical_substances_movements",
        "stg.stg_chemical_substances_declaration"
    ]
    
    results = []
    try:
        for table in tables:
            query = f"SELECT count(*) FROM {table};"
            res = pd.read_sql(query, engine_dw)
            results.append({"table": table, "count": res.iloc[0,0]})
        
        df = pd.DataFrame(results)
        print("Staging Table Counts:")
        print(df)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_stg_counts()
