import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os
import gc
import logging

# Add ETL_p dir to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ETL_p'))
from config import CONN_SUIA_ENLISY, CONN_DWH_LOCAL

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("MINIMAL_INGESTA")

def get_engines():
    uri_suia = f"postgresql://{CONN_SUIA_ENLISY['user']}:{CONN_SUIA_ENLISY['password']}@{CONN_SUIA_ENLISY['host']}:{CONN_SUIA_ENLISY['port']}/{CONN_SUIA_ENLISY['database']}"
    uri_local = f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}"
    return create_engine(uri_suia), create_engine(uri_local)

def run_ingesta():
    engine_suia, engine_local = get_engines()
    chunk_size = 10000
    
    # 1. Limpiar tabla destino
    logger.info("Limpiando stg.stg_fact_waste_generation...")
    with engine_local.connect() as conn:
        conn.execute(text("DELETE FROM stg.stg_fact_waste_generation"))
        try: conn.commit() 
        except: pass
        
    # 2. Ingesta RCOA
    query_rcoa = """
        SELECT 'SN-PROY' as project_code, lp.id_proyect as lp_id_proyect, lp.prco_id as lp_prco_id,
               w.ware_id as waste_generator_id, w.ware_creation_date as date_generated, pt.wada_id as waste_type_id,
               NULL::int as dangerous_waste_id, NULL::int as danger_class_id, NULL::int as location_id,
               pt.wwgp_quantity_kilograms as quantity_generated, pt.wwgp_quantity_kilograms as quantity_delivered, 
               0::numeric as quantity_stored, 'KG' as unit, EXTRACT(YEAR FROM w.ware_creation_date) as record_year, 'RCOA' as source_system
        FROM coa_waste_generator_record.waste_generator_record_coa w
        LEFT JOIN coa_waste_generator_record.waste_generator_record_project_licencing_coa lp ON w.ware_id = lp.ware_id
        JOIN coa_waste_generator_record.waste_waste_generation_points pt ON w.ware_id = pt.ware_id
    """
    logger.info("Extrayendo RCOA en bloques...")
    for chunk in pd.read_sql(query_rcoa, engine_suia, chunksize=chunk_size):
        chunk['lp_id_proyect'] = pd.to_numeric(chunk['lp_id_proyect'], errors='coerce').fillna(-1).astype(int)
        chunk['lp_prco_id'] = pd.to_numeric(chunk['lp_prco_id'], errors='coerce').fillna(-1).astype(int)
        chunk.to_sql('stg_fact_waste_generation', engine_local, schema='stg', if_exists='append', index=False)
        del chunk
        gc.collect()
    logger.info("RCOA Completado.")

    # 3. Ingesta COA
    query_coa = """
        SELECT COALESCE(pel.pren_code, 'SN-PROY') as project_code, COALESCE(pel.pren_id, -1) as project_id,
               hwg.hwge_id as waste_generator_id, hwg.hwge_creation_date as date_generated, hwwd.wada_id as waste_type_id,
               NULL::int as dangerous_waste_id, NULL::int as danger_class_id, NULL::int as location_id,
               COALESCE(gd.hwwg_quantity_tons, 0) * 1000 as quantity_generated, COALESCE(gd.hwwg_quantity_tons, 0) * 1000 as quantity_delivered,
               0::numeric as quantity_stored, 'KG' as unit, EXTRACT(YEAR FROM hwg.hwge_creation_date) as record_year, 'COA' as source_system
        FROM suia_iii.hazardous_wastes_generators hwg
        LEFT JOIN suia_iii.projects_environmental_licensing pel ON hwg.pren_id = pel.pren_id
        JOIN suia_iii.hazardous_wastes_waste_dangerous hwwd ON hwg.hwge_id = hwwd.hwge_id
        LEFT JOIN suia_iii.hazardous_wastes_waste_dangerous_general_data gd ON hwwd.hwwg_id = gd.hwwg_id
        WHERE hwg.hwge_status = TRUE
    """
    logger.info("Extrayendo COA en bloques...")
    for chunk in pd.read_sql(query_coa, engine_suia, chunksize=chunk_size):
        chunk.to_sql('stg_fact_waste_generation', engine_local, schema='stg', if_exists='append', index=False)
        del chunk
        gc.collect()
    logger.info("COA Completado.")

    # 4. Ingesta Mapping
    query_map = """
        SELECT ware_id, prco_id, id_proyect, wapr_description_system 
        FROM coa_waste_generator_record.waste_generator_record_project_licencing_coa 
        WHERE wapr_status = TRUE
    """
    logger.info("Actualizando stg_rgd_project_mapping...")
    df_map = pd.read_sql(query_map, engine_suia)
    df_map['prco_id'] = pd.to_numeric(df_map['prco_id'], errors='coerce').fillna(-1).astype(int)
    df_map['id_proyect'] = pd.to_numeric(df_map['id_proyect'], errors='coerce').fillna(-1).astype(int)
    df_map.to_sql('stg_rgd_project_mapping', engine_local, schema='stg', if_exists='replace', index=False)
    logger.info("Mapping completado. FIN.")

if __name__ == "__main__":
    run_ingesta()
