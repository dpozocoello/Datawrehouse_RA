import os
import sys
from sqlalchemy import create_engine, text

# Add ETL_p to path to get config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ETL_p'))
from config import CONN_DWH_LOCAL

def force_cleanup():
    uri = f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}"
    engine = create_engine(uri)
    
    with engine.connect() as conn:
        print("Intentando eliminar restricciones antiguas en dw.fact_waste_generation...")
        try:
            # 1. Eliminar restricciones conocidas por nombre
            conn.execute(text("ALTER TABLE dw.fact_waste_generation DROP CONSTRAINT IF EXISTS unique_waste_generation CASCADE;"))
            conn.execute(text("ALTER TABLE dw.fact_waste_generation DROP CONSTRAINT IF EXISTS fact_waste_generation_unique_key CASCADE;"))
            
            # 2. Buscar y eliminar dinámicamente cualquier otra restricción de unicidad que NO sea la nueva (v2)
            cleanup_query = """
            DO $$ 
            DECLARE 
                r RECORD;
            BEGIN 
                FOR r IN (
                    SELECT conname 
                    FROM pg_constraint 
                    WHERE conrelid = 'dw.fact_waste_generation'::regclass 
                    AND contype = 'u'
                    AND conname != 'fact_waste_generation_pk_v2'
                ) LOOP
                    EXECUTE 'ALTER TABLE dw.fact_waste_generation DROP CONSTRAINT ' || r.conname;
                    RAISE NOTICE 'Dropped constraint: %', r.conname;
                END LOOP;
            END $$;
            """
            conn.execute(text(cleanup_query))
            conn.commit()
            print("SUCCESS: Restricciones antiguas eliminadas correctamente.")
        except Exception as e:
            print(f"ERROR durante la limpieza: {e}")

if __name__ == "__main__":
    force_cleanup()
