
import psycopg2

def test_insert():
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
        -- Test isolated logic
        DO $$
        DECLARE
            v_sk_proyecto BIGINT;
        BEGIN
            -- Try to run just the INSERT part
            INSERT INTO dw.fact_chemical_import (
                sk_proyecto, chemical_key, importer_key, sk_tiempo, geo_location_key,
                quantity_authorized, net_weight, gross_weight, import_status, 
                processing_code, document_number, source_system
            )
            SELECT 
                0, -- fake project for test
                0, -- fake chem
                0, -- fake importer
                20240101, -- fake date
                0, -- fake geo
                100.0, 100.0, 100.0,
                'TEST', 'PROC123', 'DOC123', 'TEST_SYS'
            ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, document_number) 
            DO UPDATE SET
                quantity_authorized = EXCLUDED.quantity_authorized;
            
            RAISE NOTICE 'Insert test success';
        END $$;
        """
        print("Running isolated test SQL...")
        cur.execute(sql)
        print("Isolated test completed successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR in isolated test: {e}")

if __name__ == "__main__":
    test_insert()
