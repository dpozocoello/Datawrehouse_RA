# ==============================================================================
# ingesta_waste_chemical.py - Ingesta de Desechos y Químicos a STG (v2.1.1 CHUNKED)
# ==============================================================================
# Ingesta masiva que cubre: RETCE (Legacy), SUIA III (Vigente), COA (Nuevo).
# Host SUIA: 172.16.0.179 | Host JBPM: 172.16.0.226
# ==============================================================================

import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os
import warnings

# Silenciar FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY, CONN_DWH_LOCAL, CONN_JBPM
from utils import medir_tiempo, get_logger

logger = get_logger(__name__)

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine_suia = create_engine(build_uri(CONN_SUIA_ENLISY))
engine_destino = create_engine(build_uri(CONN_DWH_LOCAL))

# Tamaño de chunk para evitar OutOfMemory en PostgreSQL MessageContext
# 200 filas × 16 cols = 3,200 params por batch (seguro para PG)
CHUNK_SIZE = 200

@medir_tiempo("INGESTA_WASTE_CHEMICAL_V2")
def ejecutar_ingesta_waste_chemical():
    logger.info("[RGD_V2.1] Iniciando ingesta integral con Puntos de Generación...")

    # 1. Consultas de Extracción - DOMINIO CORE
    queries_core = {
        "stg_waste_generator": """
            SELECT hwg.hwge_id as waste_generator_id, 'SUIA_III' as source_system,
                   hwg.hwge_code as registry_number, u.user_name as ruc,
                   hwg.hwge_creation_date as date_add, hwg.pren_id as proj_id,
                   NULL as generator_name, NULL as generator_type, NULL as province, NULL as canton,
                   hwg.hwge_creation_date as date_update
            FROM suia_iii.hazardous_wastes_generators hwg
            LEFT JOIN public.users u ON hwg.user_id = u.user_id
            WHERE hwg.hwge_id IS NOT NULL
            UNION ALL
            SELECT w.ware_id as waste_generator_id, 'COA' as source_system,
                   w.ware_code as registry_number, u.user_name as ruc,
                   w.ware_creation_date as date_add, lp.id_proyect as proj_id,
                   NULL as generator_name, NULL as generator_type, NULL as province, NULL as canton,
                   w.ware_creation_date as date_update
            FROM coa_waste_generator_record.waste_generator_record_coa w
            LEFT JOIN public.users u ON w.user_id = u.user_id
            LEFT JOIN coa_waste_generator_record.waste_generator_record_project_licencing_coa lp ON w.ware_id = lp.ware_id
            WHERE w.ware_status = TRUE AND w.ware_id IS NOT NULL
        """,
        "stg_waste_catalogs_parent": "SELECT cawp_id, cawp_key, cawp_name, cawp_status FROM waste_dangerous.catalogs_waste_parent",
        "stg_waste_type": "SELECT cawa_id, cawp_id, cawa_key, cawa_name, cawa_status FROM waste_dangerous.catalogs_waste",
        "stg_generation_points": """
            -- Puntos en COA (Nuevo)
            SELECT wwgp_id as source_id, 'RCOA' as source_system, ware_id as waste_generator_id,
                   NULL as point_name, NULL::double precision as x_coordinate, NULL::double precision as y_coordinate,
                   NULL as province, NULL as canton, NULL as parroquia
            FROM coa_waste_generator_record.waste_waste_generation_points
            UNION ALL
            -- Puntos Virtuales en SUIA III (Vigente)
            SELECT hwge_id as source_id, 'COA' as source_system, hwge_id as waste_generator_id,
                   'Punto Principal' as point_name, NULL::double precision as x_coordinate, NULL::double precision as y_coordinate,
                   NULL as province, NULL as canton, NULL as parroquia
            FROM suia_iii.hazardous_wastes_generators
        """
    }

    # 1.1 Intentar catálogos opcionales
    optional_catalogs = {
        "stg_dangerous_waste": "SELECT dw_id, dangerous_code, description, regulation_reference FROM waste_dangerous.dangerous_waste WHERE is_active = TRUE",
        "stg_dangerous_classification": "SELECT class_id, danger_level, description FROM waste_dangerous.dw_classification"
    }
    
    fallbacks = {
        "stg_dangerous_waste": "SELECT wada_id as dw_id, wada_key as dangerous_code, wada_name as description, NULL as regulation_reference FROM suia_iii.waste_dangerous",
        "stg_dangerous_classification": "SELECT NULL as class_id, NULL as danger_level, NULL as description LIMIT 0"
    }

    # 2. Consultas de Extracción - DOMINIO GEOGRÁFICO
    queries_geo = {
        "stg_rgd_warehouses": """
            SELECT repo_id as hwwa_id, hwge_id, repo_name as hwwa_name,
                   NULL::double precision as hwwa_x_coordinate,
                   NULL::double precision as hwwa_y_coordinate,
                   NULL as hwwa_province, NULL as hwwa_canton, repo_status as hwwa_status
            FROM suia_iii.recovery_points
        """
    }

    # 3. Consultas de Extracción - DOMINIO HECHOS (Generación con Punto ID)
    queries_fact = {
        "stg_fact_waste_generation": """
            -- COA (SUIA III)
            SELECT COALESCE(pel.pren_code, 'SN-PROY') as project_code, COALESCE(pel.pren_id, -1) as project_id,
                   hwg.hwge_id as waste_generator_id, hwg.hwge_id as point_id, hwg.hwge_creation_date as date_generated, hwwd.wada_id as waste_type_id,
                   NULL::int as dangerous_waste_id, NULL::int as danger_class_id, NULL::int as location_id,
                   COALESCE(gd.hwwg_quantity_tons, 0) * 1000 as quantity_generated, COALESCE(gd.hwwg_quantity_tons, 0) * 1000 as quantity_delivered,
                   0::numeric as quantity_stored, 'KG' as unit, EXTRACT(YEAR FROM hwg.hwge_creation_date) as record_year, 'COA' as source_system
            FROM suia_iii.hazardous_wastes_generators hwg
            LEFT JOIN suia_iii.projects_environmental_licensing pel ON hwg.pren_id = pel.pren_id
            JOIN suia_iii.hazardous_wastes_waste_dangerous hwwd ON hwg.hwge_id = hwwd.hwge_id
            LEFT JOIN suia_iii.hazardous_wastes_waste_dangerous_general_data gd ON hwwd.hwwg_id = gd.hwwg_id
            WHERE hwg.hwge_status = TRUE
            UNION ALL
            -- RCOA (COA New)
            SELECT COALESCE(lp.wapr_description_system, 'SN-PROY') as project_code, lp.id_proyect as project_id, 
                   w.ware_id as waste_generator_id, pt.wwgp_id as point_id, w.ware_creation_date as date_generated, pt.wada_id as waste_type_id,
                   NULL::int as dangerous_waste_id, NULL::int as danger_class_id, NULL::int as location_id,
                   pt.wwgp_quantity_kilograms as quantity_generated, pt.wwgp_quantity_kilograms as quantity_delivered, 
                   0::numeric as quantity_stored, 'KG' as unit, EXTRACT(YEAR FROM w.ware_creation_date) as record_year, 'RCOA' as source_system
            FROM coa_waste_generator_record.waste_generator_record_coa w
            LEFT JOIN coa_waste_generator_record.waste_generator_record_project_licencing_coa lp ON w.ware_id = lp.ware_id
            JOIN coa_waste_generator_record.waste_waste_generation_points pt ON w.ware_id = pt.ware_id
            WHERE w.ware_status = TRUE AND w.ware_id IS NOT NULL
        """
    }

    try:
        # Ingesta CORE, GEOGRAFÍA y Puntos
        for target_table, query in {**queries_core, **queries_geo}.items():
            logger.info(f"   - Extrayendo {target_table}...")
            df = pd.read_sql(query, engine_suia)
            df.to_sql(target_table, engine_destino, schema="stg", if_exists="replace", index=False, chunksize=CHUNK_SIZE, method='multi')
            logger.info(f"   - {len(df)} filas cargadas en stg.{target_table} (chunks de {CHUNK_SIZE})")

        # Ingesta de Catálogos Opcionales
        for target_table, query in optional_catalogs.items():
            logger.info(f"   - Extrayendo {target_table} (opcional)...")
            try:
                df = pd.read_sql(query, engine_suia)
            except Exception as e:
                logger.warning(f"     ! Fallo inicial en {target_table}, intentando fallback...")
                try:
                    df = pd.read_sql(fallbacks[target_table], engine_suia)
                except:
                    logger.error(f"     !! Fallo total en {target_table}, cargando estructura vacía.")
                    df = pd.DataFrame()
            
            df.to_sql(target_table, engine_destino, schema="stg", if_exists="replace", index=False, chunksize=CHUNK_SIZE, method='multi')
            logger.info(f"   - {len(df)} filas cargadas en stg.{target_table} (chunks de {CHUNK_SIZE})")

        # Ingesta de FACT (Consolidada) — CHUNKED para evitar OOM
        for target_table, query in queries_fact.items():
            logger.info(f"   - Extrayendo {target_table} (tabla grande, chunks de {CHUNK_SIZE})...")
            df = pd.read_sql(query, engine_suia)
            total_rows = len(df)
            logger.info(f"   - Extraídas {total_rows} filas, iniciando carga por lotes...")
            df.to_sql(target_table, engine_destino, schema="stg", if_exists="replace", index=False, chunksize=CHUNK_SIZE, method='multi')
            logger.info(f"   ✓ {total_rows} filas cargadas en stg.{target_table} ({(total_rows // CHUNK_SIZE) + 1} batches)")

        logger.info("[RGD_V2.1] Ingesta finalizada exitosamente.")
        return True

    except Exception as e:
        logger.error(f"[RGD_ERROR] Error en ingesta v2.1.0: {e}")
        raise

if __name__ == "__main__":
    ejecutar_ingesta_waste_chemical()
