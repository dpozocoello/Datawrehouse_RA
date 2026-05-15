import pandas as pd
from sqlalchemy import create_engine, text

CONN_SUIA_ENLISY = {
    "host": "172.16.0.179",
    "port": 5632,
    "database": "suia_enlisy",
    "user": "postgres",
    "password": "postgres",
}

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine = create_engine(build_uri(CONN_SUIA_ENLISY))

def test_query():
    query = text("""
        SELECT 
            plc.prco_cua as project_code,
            lc.laye_id,
            lc.laye_name
        FROM coa_mae.intersections_project_licencing_coa iplc
        JOIN coa_mae.project_licencing_coa plc ON iplc.prco_id = plc.prco_id
        JOIN coa_mae.layers_coa lc ON iplc.laye_id = lc.laye_id
        WHERE iplc.inpr_status = TRUE
        LIMIT 10
    """)
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            print(df)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query()
