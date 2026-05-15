
import sqlalchemy as sa
import pandas as pd

def check_cols():
    uri = "postgresql://postgres:postgres@172.16.0.179:5632/suia_enlisy"
    engine = sa.create_engine(uri)
    
    try:
        query = "SELECT * FROM coa_chemical_sustances.chemical_sustances_records LIMIT 1;"
        df = pd.read_sql(query, engine)
        print("Columns in chemical_sustances_records:")
        print(df.columns.tolist())
        
        # Check if there is a company identification column
        id_cols = [c for c in df.columns if 'ident' in c.lower() or 'ruc' in c.lower() or 'code' in c.lower()]
        print("\nPotential ID columns:")
        print(id_cols)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cols()
