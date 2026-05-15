
import sqlalchemy as sa
import pandas as pd

def audit_v4():
    uri = "postgresql://postgres:postgres@172.16.0.179:5632/suia_enlisy"
    engine = sa.create_engine(uri)
    
    try:
        # Check chsr_code format
        print("--- Sampling chsr_code from chemical_sustances_records ---")
        query_code = "SELECT chsr_code, prco_id FROM coa_chemical_sustances.chemical_sustances_records WHERE chsr_code IS NOT NULL LIMIT 10;"
        df_code = pd.read_sql(query_code, engine)
        print(df_code)
        
        # Check if codes looks like CUAs
        if not df_code.empty:
            sample_codes = tuple(df_code['chsr_code'].tolist())
            query_cua = f"SELECT prco_id, prco_cua FROM coa_mae.project_licencing_coa WHERE prco_cua IN {sample_codes};"
            df_cua = pd.read_sql(query_cua, engine)
            print("\nMatching chsr_code to coa_mae.project_licencing_coa (prco_cua):")
            print(df_cua)
            
        # Check technical_analysis
        print("\n--- Sampling coa_chemical_sustances.technical_analysis ---")
        query_tech = "SELECT * FROM coa_chemical_sustances.technical_analysis LIMIT 5;"
        df_tech = pd.read_sql(query_tech, engine)
        print(df_tech)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_v4()
