# ==============================================================================
# ingesta_waste_chemical.py - Ingesta de Desechos y Químicos a STG (v1.6.7 FINAL)
# ==============================================================================
# Ingesta unificada de RGD (COA Legacy + RCOA Nuevo) con RCOA LEFT JOIN por CUA.
# Host SUIA: 172.16.0.179 | Host JBPM: 172.16.0.226
# ==============================================================================

import pandas as pd
from sqlalchemy import create_engine
import sys
import os
import warnings

# Silenciar FutureWarnings de Pandas (especialmente concatenaciones con columnas NA)
warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY, CONN_DWH_LOCAL, CONN_JBPM
from utils import medir_tiempo, get_logger

logger = get_logger(__name__)

# Configurar engines de SQLAlchemy
def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine_suia = create_engine(build_uri(CONN_SUIA_ENLISY))
engine_jbpm = create_engine(build_uri(CONN_JBPM))
engine_destino = create_engine(build_uri(CONN_DWH_LOCAL))

@medir_tiempo("INGESTA_WASTE_CHEMICAL")
def ejecutar_ingesta_waste_chemical():
    logger.info("[INGESTA_WASTE_CHEMICAL] Iniciando ingesta v1.6.7 (ROBUSTEZ CON LEFT JOIN)...")

    # 1. Extracciones desde SUIA (Servidor 179)
    # Se dividen para evitar problemas de alineamiento de columnas en UNION ALL complejos
    queries_suia = {
        "stg_waste_generator_rcoa": """
            SELECT w.ware_id as waste_generator_id, w.ware_code as generator_name, 'RCOA' as generator_type,
                   u.user_name as ruc_generator, u.user_docu_id as identification_type,
                   NULL as province, NULL as canton, w.ware_creation_date as date_add, w.ware_date_update as date_update
            FROM coa_waste_generator_record.waste_generator_record_coa w
            LEFT JOIN public.users u ON w.user_id = u.user_id WHERE w.ware_status = TRUE
        """,
        "stg_waste_generator_coa": """
            SELECT hwg.hwge_id as waste_generator_id, COALESCE(pel.pren_name, 'GENERADOR_SIN_LICENCIA') as generator_name, 'COA' as generator_type,
                   COALESCE(pel.pren_code, 'SN-' || hwg.hwge_id::text) as ruc_generator, 'RUC' as identification_type,
                   NULL as province, NULL as canton, hwg.hwge_creation_date as date_add, NULL as date_update
            FROM suia_iii.hazardous_wastes_generators hwg
            LEFT JOIN suia_iii.projects_environmental_licensing pel ON hwg.pren_id = pel.pren_id
        """,
        "stg_fact_waste_rcoa": """
            SELECT 'SN-PROY' as project_code, lp.id_proyect as lp_id_proyect, lp.prco_id as lp_prco_id,
                   w.ware_id as waste_generator_id, w.ware_creation_date as date_generated, pt.wada_id as waste_type_id,
                   NULL::int as dangerous_waste_id, NULL::int as danger_class_id, NULL::int as location_id,
                   pt.wwgp_quantity_kilograms as quantity_generated, pt.wwgp_quantity_kilograms as quantity_delivered, 
                   0::numeric as quantity_stored, 'KG' as unit, EXTRACT(YEAR FROM w.ware_creation_date) as record_year, 'RCOA' as source_system
            FROM coa_waste_generator_record.waste_generator_record_coa w
            LEFT JOIN coa_waste_generator_record.waste_generator_record_project_licencing_coa lp ON w.ware_id = lp.ware_id
            JOIN coa_waste_generator_record.waste_waste_generation_points pt ON w.ware_id = pt.ware_id
        """,
        "stg_fact_waste_coa": """
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
        """,
        "stg_rgd_project_mapping": """
            SELECT ware_id, prco_id, id_proyect, wapr_description_system 
            FROM coa_waste_generator_record.waste_generator_record_project_licencing_coa 
            WHERE wapr_status = TRUE
        """
    }

    # Catálogos (se mantienen igual pero en diccionario separado)
    catalog_queries = {
        "stg_waste_type": "SELECT cawa_id, cawa_key as waste_key_code, cawa_name as waste_name, cawa_status as waste_status FROM waste_dangerous.catalogs_waste",
        "stg_dangerous_waste": "SELECT cawp_id as dw_id, cawp_key as dangerous_code, cawp_name as description, 'CATALOGO_PADRE' as regulation_reference FROM waste_dangerous.catalogs_waste_parent WHERE cawp_status = TRUE",
        "stg_dangerous_classification": "SELECT cata_id as class_id, cata_description as danger_level, cata_description as description FROM waste_dangerous.catalogs WHERE cata_status = TRUE",
        "stg_chemical_substance": """
            SELECT chsr_id as chemical_id, chsr_code as substance_name, chsr_code as cas_number, 'SUSTANCIA_COA' as classification, 'CHEMICAL' as chemical_type FROM coa_chemical_sustances.chemical_sustances_records
            UNION ALL
            SELECT prod_id as chemical_id, prod_trade_name_product as substance_name, prod_register_number as cas_number, prod_toxicological_category as classification, 'PESTICIDE' as chemical_type FROM chemical_pesticides.products_pqa
        """
    }


    # 2. Extracciones desde JBPM (Servidor 226)
    jbpm_extracts = {
        "stg.online_payments_historical_bi": """
            SELECT 
                id_online_payment_historical, description, project_id, retired_value, 
                sender_ip, tramit_number, update_date, value_updated, online_payment_id, 
                enabled, user_create, user_modification, date_create, date_modification, 
                reactivate, observations
            FROM online_payment.online_payments_historical
        """
    }

    try:
        # 1. Ingesta de Generadores (Unificada via Concat)
        logger.info("[INGESTA_SUIA] -> Procesando Generadores (RCOA + COA)...")
        df_gen_rcoa = pd.read_sql(queries_suia["stg_waste_generator_rcoa"], engine_suia)
        df_gen_coa = pd.read_sql(queries_suia["stg_waste_generator_coa"], engine_suia)
        
        # FIX: Evitar FutureWarning filtrando DataFrames vacíos antes del concat
        df_to_concat_gen = [d for d in [df_gen_rcoa, df_gen_coa] if not d.empty]
        if df_to_concat_gen:
            df_gen = pd.concat(df_to_concat_gen, ignore_index=True)
        else:
            # Si ambos están vacíos, crear DF vacío con las columnas correctas
            df_gen = df_gen_rcoa.copy()
            
        df_gen.columns = [str(c) for c in df_gen.columns]
        df_gen.to_sql('stg_waste_generator', engine_destino, schema='stg', if_exists='replace', index=False)
        logger.info(f"[INGESTA_SUIA] Generadores cargados: {len(df_gen)} (RCOA: {len(df_gen_rcoa)}, COA: {len(df_gen_coa)})")

        # 2. Ingesta de Hechos (Unificada via Concat con CHUNKING)
        logger.info("[INGESTA_SUIA] -> Procesando Hechos de Generación (RCOA + COA) en bloques...")
        
        # Limpiar tabla destino antes de append
        from sqlalchemy import text
        with engine_destino.connect() as conn:
            conn.execute(text("TRUNCATE TABLE stg.stg_fact_waste_generation"))
            try:
                conn.commit()
            except:
                pass # SQLAlchemy 1.x handles this differently
        
        # Procesar RCOA
        logger.info("[INGESTA_SUIA] -> Extrayendo RCOA...")
        chunk_size = 50000
        for chunk in pd.read_sql(queries_suia["stg_fact_waste_rcoa"], engine_suia, chunksize=chunk_size):
            chunk.columns = [str(c) for c in chunk.columns]
            # CASTING: Asegurar que los IDs sean enteros para joins eficientes
            if 'lp_id_proyect' in chunk.columns:
                chunk['lp_id_proyect'] = pd.to_numeric(chunk['lp_id_proyect'], errors='coerce').fillna(-1).astype(int)
            if 'lp_prco_id' in chunk.columns:
                chunk['lp_prco_id'] = pd.to_numeric(chunk['lp_prco_id'], errors='coerce').fillna(-1).astype(int)
                
            chunk.to_sql('stg_fact_waste_generation', engine_destino, schema='stg', if_exists='append', index=False)
            logger.info(f"   - Bloque RCOA guardado ({len(chunk)} filas).")
            
        # Procesar COA
        logger.info("[INGESTA_SUIA] -> Extrayendo COA...")
        for chunk in pd.read_sql(queries_suia["stg_fact_waste_coa"], engine_suia, chunksize=chunk_size):
            chunk.columns = [str(c) for c in chunk.columns]
            chunk.to_sql('stg_fact_waste_generation', engine_destino, schema='stg', if_exists='append', index=False)
            logger.info(f"   - Bloque COA guardado ({len(chunk)} filas).")

        # 3. Ingesta de Tabla de Mapeo RGD (NUEVO)
        logger.info("[INGESTA_SUIA] -> Procesando Tabla de Mapeo RGD...")
        df_map_rgd = pd.read_sql(queries_suia["stg_rgd_project_mapping"], engine_suia)
        # CASTING: Consistencia con Hechos
        if 'prco_id' in df_map_rgd.columns:
            df_map_rgd['prco_id'] = pd.to_numeric(df_map_rgd['prco_id'], errors='coerce').fillna(-1).astype(int)
        if 'id_proyect' in df_map_rgd.columns:
            df_map_rgd['id_proyect'] = pd.to_numeric(df_map_rgd['id_proyect'], errors='coerce').fillna(-1).astype(int)
            
        df_map_rgd.to_sql('stg_rgd_project_mapping', engine_destino, schema='stg', if_exists='replace', index=False)
        logger.info(f"[INGESTA_SUIA] Mapping RGD cargado: {len(df_map_rgd)} filas.")

        # 4. Ingesta de Catálogos
        for tabla, query in catalog_queries.items():
            logger.info(f"[INGESTA_SUIA] -> Catálogo {tabla}...")
            df = pd.read_sql(query, engine_suia)
            df.columns = [str(c) for c in df.columns]
            df.to_sql(tabla.replace('stg.', ''), engine_destino, schema='stg', if_exists='replace', index=False)
            logger.info(f"[INGESTA_SUIA] Catálogo {tabla} OK ({len(df)} filas).")

        # 4. Ingesta de JBPM (Pagos)
        for tabla_destino, query in jbpm_extracts.items():
            logger.info(f"[INGESTA_JBPM] -> {tabla_destino}...")
            df = pd.read_sql(query, engine_jbpm)
            df.columns = [str(c) for c in df.columns]
            if 'retired_value' in df.columns: df['retired_value'] = pd.to_numeric(df['retired_value'], errors='coerce')
            if 'value_updated' in df.columns: df['value_updated'] = pd.to_numeric(df['value_updated'], errors='coerce')
            df.to_sql(tabla_destino.split('.')[-1], engine_destino, schema='stg', if_exists='replace', index=False)
            logger.info(f"[INGESTA_JBPM] {len(df)} filas cargadas.")

    except Exception as e:
        logger.error(f"[INGESTA_ERROR] = {e}")
        raise

    return True

if __name__ == "__main__":
    ejecutar_ingesta_waste_chemical()
