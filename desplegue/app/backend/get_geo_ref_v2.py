
import psycopg2
import pandas as pd

def get_ecuador_geography():
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")
        
        # Level 1: ECUADOR
        # Level 2: Provinces
        # Level 3: Cantons
        query = """
        SELECT c.gelo_name as canton, p.gelo_name as provincia, p.gelo_codification_inec as province_code
        FROM stg.geographical_locations_bi c
        JOIN stg.geographical_locations_bi p ON c.gelo_parent_id = p.gelo_id
        WHERE c.level = 3 AND p.level = 2;
        """
        df = pd.read_sql(query, conn)
        print("--- ECUADOR CANTONS & PROVINCES ---")
        print(len(df))
        print(df.head(10))
        
        df.to_csv("f:/Datawrehouse_RA/ecuador_geo_reference.csv", index=False)
        print("\nSaved reference to f:/Datawrehouse_RA/ecuador_geo_reference.csv")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_ecuador_geography()
