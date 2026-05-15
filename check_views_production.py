
import sqlalchemy as sa
import pandas as pd

def check_views():
    uri = "postgresql://postgres:postgres@172.16.0.179:5632/suia_enlisy"
    engine = sa.create_engine(uri)
    
    try:
        # Check the definition of the view if possible, or just sample it
        print("--- Sampling coa_chemical_sustances.vw_proyectos_declaracion ---")
        df = pd.read_sql("SELECT * FROM coa_chemical_sustances.vw_proyectos_declaracion LIMIT 10", engine)
        print(df)
        
        print("\n--- Sampling coa_chemical_sustances.vw_registro_sustancia_quimica ---")
        df2 = pd.read_sql("SELECT * FROM coa_chemical_sustances.vw_registro_sustancia_quimica LIMIT 10", engine)
        print(df2)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_views()
