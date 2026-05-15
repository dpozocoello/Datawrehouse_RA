import psycopg2
import sys
import os

sys.path.insert(0, r'd:\Datawrehouse_RA\ETL_p')
from config import CONN_DWH_LOCAL

def create_tables():
    try:
        conn = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'],
            port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'],
            user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn.cursor()
        
        print("Creating schemas and tables...")
        cur.execute("CREATE SCHEMA IF NOT EXISTS stg;")
        cur.execute("CREATE SCHEMA IF NOT EXISTS dw;")
        
        print("Dropping existing tables for schema update...")
        cur.execute("DROP TABLE IF EXISTS stg.stg_intersection CASCADE;")
        cur.execute("DROP TABLE IF EXISTS dw.dim_intersection CASCADE;")
        
        # Staging
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stg.stg_intersection (
                project_code varchar(100),
                certificate_code varchar(100),
                certificate_date timestamp,
                html_location text,
                html_layers text,
                dictamen_final text
            );
        """)
        
        # Dimension
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dw.dim_intersection (
                sk_intersection serial primary key,
                sk_proyecto integer,
                certificate_code varchar(100),
                certificate_date timestamp,
                html_location text,
                html_layers text,
                dictamen_final text,
                is_current boolean default true,
                effective_from timestamp default current_timestamp,
                UNIQUE (sk_proyecto, certificate_code)
            );
        """)
        
        conn.commit()
        print("Tables and constraints created successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_tables()
