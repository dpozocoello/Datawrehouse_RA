
import psycopg2
import sys

def test_insert_verbose():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        sql = """
        INSERT INTO dw.fact_chemical_import (
            sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
            quantity_authorized, net_weight, gross_weight, import_status, 
            processing_code, document_number, source_system
        )
        VALUES (
            0, 0, 0, 20240101, 0,
            100.0, 100.0, 100.0,
            'TEST', 'PROC123', 'DOC123', 'TEST_SYS'
        )
        ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number) 
        DO UPDATE SET
            quantity_authorized = EXCLUDED.quantity_authorized;
        """
        print("Running isolated test SQL (Verbose Error)...")
        cur.execute(sql)
        print("SUCCESS!")
        conn.commit()
        
    except psycopg2.Error as e:
        print(f"Postgres Error: {e.pgerror}")
        print(f"Postgres Code: {e.pgcode}")
    except Exception as e:
        print(f"Other Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    test_insert_verbose()
