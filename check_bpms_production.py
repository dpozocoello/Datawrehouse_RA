
import sqlalchemy as sa
import pandas as pd

def check_bpms():
    uri = "postgresql://postgres:postgres@172.16.0.179:5632/suia_bpms_enlisy_app"
    engine = sa.create_engine(uri)
    
    query = """
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY table_schema, table_name;
    """
    try:
        df = pd.read_sql(query, engine)
        print("Tables in suia_bpms_enlisy_app:")
        print(df)
        
        # Look for process related to chemicals
        query_proc = """
        SELECT * FROM public.processinstanceinfo LIMIT 5;
        """
        # (Assuming public schema and processinstanceinfo table exists based on standard jBPM/BPMS naming)
        # I'll just check if it exists first
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_bpms()
