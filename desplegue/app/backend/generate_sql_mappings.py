
import pandas as pd

def generate_sql_mappings():
    df = pd.read_csv("f:/Datawrehouse_RA/proposed_geo_fix_v1_4.csv")
    
    print("--- PROVINCE FALLBACK ---")
    for _, row in df.iterrows():
        print(f"WHEN s.area_id = {int(row['id_area'])} THEN '{row['prov_sug']}' -- {row['name']}")
        
    print("\n--- CANTON FALLBACK ---")
    for _, row in df.iterrows():
        print(f"WHEN s.area_id = {int(row['id_area'])} THEN '{row['cant_sug']}'")

if __name__ == "__main__":
    generate_sql_mappings()
