
import sqlalchemy as sa
import pandas as pd

def audit_v3():
    uri = "postgresql://postgres:postgres@172.16.0.179:5632/suia_enlisy"
    engine = sa.create_engine(uri)
    
    try:
        # Get sample orphan prco_ids
        query_orphans = """
        SELECT r.prco_id, count(*) 
        FROM coa_chemical_sustances.chemical_sustances_records r
        LEFT JOIN coa_mae.project_licencing_coa p ON r.prco_id = p.prco_id
        WHERE p.prco_id IS NULL
        GROUP BY r.prco_id
        LIMIT 10;
        """
        df_orphans = pd.read_sql(query_orphans, engine)
        print("Sample Orphan prco_ids from chemical_sustances_records:")
        print(df_orphans)
        
        if not df_orphans.empty:
            sample_ids = tuple(df_orphans['prco_id'].tolist())
            
            # Check if they exist in project_names or other tables
            tables_to_check = [
                ('coa_mae', 'project_names'),
                ('coa_mae', 'projects'),
                ('public', 'projects'),
                ('public', 'project_names')
            ]
            
            for schema, table in tables_to_check:
                try:
                    query_check = f"SELECT count(*) FROM {schema}.{table} WHERE id IN {sample_ids};"
                    res = pd.read_sql(query_check, engine)
                    print(f"Match in {schema}.{table}: {res.iloc[0,0]}")
                except:
                    # Column might be different name, try common names
                    for col in ['id', 'proj_id', 'prco_id', 'project_id']:
                        try:
                            query_check = f"SELECT count(*) FROM {schema}.{table} WHERE {col} IN {sample_ids};"
                            res = pd.read_sql(query_check, engine)
                            print(f"Match in {schema}.{table} (col {col}): {res.iloc[0,0]}")
                            break
                        except:
                            continue

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_v3()
