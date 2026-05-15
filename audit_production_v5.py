
import sqlalchemy as sa
import pandas as pd

def audit_v5():
    uri_prod = "postgresql://postgres:postgres@172.16.0.179:5632/suia_enlisy"
    uri_dw = "postgresql://postgres:postgres@localhost:5432/dw_reg_v1"
    
    engine_prod = sa.create_engine(uri_prod)
    engine_dw = sa.create_engine(uri_dw)
    
    try:
        # Get RUCs from orphan chemical records in production
        query_rucs = """
        SELECT DISTINCT chsr_identification_rep_legal as ruc
        FROM coa_chemical_sustances.chemical_sustances_records
        WHERE prco_id IS NULL AND chsr_identification_rep_legal IS NOT NULL;
        """
        df_rucs = pd.read_sql(query_rucs, engine_prod)
        print(f"Total distinct RUCs in orphan records: {len(df_rucs)}")
        
        if not df_rucs.empty:
            rucs = tuple(df_rucs['ruc'].tolist())
            # Check if these RUCs exist in local DW (dim_proponente)
            query_dw = f"SELECT count(*) FROM dw.dim_proponente WHERE ced_ruc_proponente IN {rucs};"
            res = pd.read_sql(query_dw, engine_dw)
            print(f"RUC matches in local DWH (dim_proponente): {res.iloc[0,0]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_v5()
