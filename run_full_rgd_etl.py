import os
import sys
import logging
from sqlalchemy import create_engine, text

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_DWH_LOCAL
from ingesta.ingesta_waste_chemical import ejecutar_ingesta_waste_chemical

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("FULL_RGD_ETL")

def get_engine():
    uri_local = f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}"
    return create_engine(uri_local)

def run_full_etl():
    logger.info("Step 1: Running Python Ingestion (Source to STG)...")
    try:
        success = ejecutar_ingesta_waste_chemical()
        if not success:
            logger.error("Python ingestion failed.")
            return
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return

    logger.info("Step 2: Running SQL Transformation (STG to DW)...")
    engine = get_engine()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sp_path = os.path.join(script_dir, 'sp_etl_waste_chemical.sql')
    
    with engine.connect() as conn:
        try:
            # First, make sure the SP is updated from the file
            if not os.path.exists(sp_path):
                logger.error(f"SQL file not found at {sp_path}")
                return

            with open(sp_path, 'r', encoding='utf-8') as f:
                sp_sql = f.read()
            conn.execute(text(sp_sql))
            logger.info("Stored Procedure updated.")
            
            # Execute the SP
            conn.execute(text("SELECT dw.sp_etl_waste_chemical();"))
            # conn.commit() # SQLAlchemy 2.0+ handles this with connect() as conn if using begin()
            try:
                conn.commit()
            except:
                pass
            logger.info("SQL Transformation completed successfully.")
        except Exception as e:
            logger.error(f"Error during SQL transformation: {e}")
            return

    logger.info("Full ETL process finished.")

if __name__ == "__main__":
    run_full_etl()
