import pandas as pd
from sqlalchemy import create_engine, text

# Probar en la otra base de datos
engine_bpms = create_engine("postgresql://postgres:postgres@172.16.0.179:5632/suia_bpms_enlisy_app")

def check_bpms():
    print("--- Buscando capas en suia_bpms_enlisy_app ---")
    query = text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name ILIKE '%layer%'")
    try:
        with engine_bpms.connect() as conn:
            df = pd.read_sql(query, conn)
            print(df)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_bpms()
