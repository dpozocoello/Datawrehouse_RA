
import sqlalchemy as sa
import pandas as pd
import sys

def audit_remote():
    host = "172.16.0.179"
    ports = [5632, 6532]
    user = "postgres"
    password = "postgres"
    
    databases = ["suia_enlisy", "suia_enlisy_bpms", "suia_bpms_enlisy_app"]
    
    working_conn = None
    
    print("--- 1. Connection Test ---")
    for port in ports:
        for db in databases:
            try:
                uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"
                engine = sa.create_engine(uri, connect_args={'connect_timeout': 5})
                with engine.connect() as conn:
                    print(f"SUCCESS: Connected to {host}:{port}/{db}")
                    working_conn = engine
                    break
            except Exception as e:
                print(f"FAILED: Connection to {host}:{port}/{db}")
        if working_conn:
            break
            
    if not working_conn:
        print("ERROR: Could not connect to any production database.")
        return

    print("\n--- 2. Chemical Metadata Audit ---")
    try:
        # Check tables in coa_chemical_sustances
        query_tables = """
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'coa_chemical_sustances'
        ORDER BY table_name;
        """
        df_tables = pd.read_sql(query_tables, working_conn)
        print("Tables in coa_chemical_sustances:")
        print(df_tables)
        
        # Check Project Mapping Consistency
        query_mapping_audit = """
        SELECT 
            'Total Records' as metric, count(*) as value
        FROM coa_chemical_sustances.chemical_sustances_records
        UNION ALL
        SELECT 
            'Orphan Projects (No Link to coa_mae)' as metric, count(*)
        FROM coa_chemical_sustances.chemical_sustances_records r
        LEFT JOIN coa_mae.project_licencing_coa p ON r.prco_id = p.prco_id
        WHERE p.prco_id IS NULL;
        """
        df_mapping = pd.read_sql(query_mapping_audit, working_conn)
        print("\nMapping Audit (Records -> coa_mae):")
        print(df_mapping)
        
        # Check Declarations Consistency
        query_declaration_audit = """
        SELECT 
            'Total Declarations' as metric, count(*) as value
        FROM coa_chemical_sustances.chemical_substances_declaration
        UNION ALL
        SELECT 
            'Orphan Declarations (No Link to Header)' as metric, count(*)
        FROM coa_chemical_sustances.chemical_substances_declaration d
        LEFT JOIN coa_chemical_sustances.chemical_sustances_records r ON d.chsr_id = r.chsr_id
        WHERE r.chsr_id IS NULL;
        """
        df_decl = pd.read_sql(query_declaration_audit, working_conn)
        print("\nDeclaration Audit (Declarations -> Header):")
        print(df_decl)

    except Exception as e:
        print(f"Audit Error: {e}")

if __name__ == "__main__":
    audit_remote()
