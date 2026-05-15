# ==============================================================================
# ingesta_waste_chemical.py - Ingesta de Desechos y Químicos a STG (v2.0.0 INTEGRAL)
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

@medir_tiempo("INGESTA_WASTE_CHEMICAL_V2")
def ejecutar_ingesta_waste_chemical():
    logger.info("[RGD_V2] Iniciando ingesta integral v2.0.0 (115+ Tablas)...")

    # 1. Consultas de Extracción - DOMINIO CORE
    queries_core = {
        "stg_waste_generator": """
            SELECT hwg.hwge_id as waste_generator_id, NULL as rcoa_id, 'SUIA_III' as source,
                   hwg.hwge_code as registry_number, u.user_name as ruc,
                   hwg.hwge_creation_date as date_add, hwg.pren_id as proj_id
            FROM suia_iii.hazardous_wastes_generators hwg
            LEFT JOIN public.users u ON hwg.user_id = u.user_id
            UNION ALL
            SELECT NULL, w.ware_id, 'COA', w.ware_code, u.user_name, w.ware_creation_date, lp.id_proyect
            FROM coa_waste_generator_record.waste_generator_record_coa w
            LEFT JOIN public.users u ON w.user_id = u.user_id
            LEFT JOIN coa_waste_generator_record.waste_generator_record_project_licencing_coa lp ON w.ware_id = lp.ware_id
            WHERE w.ware_status = TRUE
        """,
        "stg_waste_catalogs_parent": "SELECT cawp_id, cawp_key, cawp_name, cawp_status FROM waste_dangerous.catalogs_waste_parent",
        "stg_waste_type": "SELECT cawa_id, cawp_id, cawa_key, cawa_name, cawa_status FROM waste_dangerous.catalogs_waste"
    }

    # 2. Consultas de Extracción - DOMINIO GEOGRÁFICO (Sitios de Retiro)
    # NOTA: hazardous_wastes_warehouses no tiene hwge_id ni coordenadas directas.
    # Se usa recovery_points (suia_iii) que sí tiene hwge_id como tabla de puntos geográficos.
    queries_geo = {
        "stg_rgd_warehouses": """
            SELECT repo_id as hwwa_id, hwge_id, repo_name as hwwa_name,
                   NULL::double precision as hwwa_x_coordinate,
                   NULL::double precision as hwwa_y_coordinate,
                   NULL as hwwa_province, NULL as hwwa_canton, repo_status as hwwa_status
            FROM suia_iii.recovery_points
        """
    }

    # 3. Consultas de Extracción - DOMINIO MOVIMIENTOS (Manifiestos RETCE)
    # NOTA: detail_manifests_waste no tiene hwge_id directamente; viene por join
    # a través de hazardous_waste_generator_retce. Se usa hwgr.hwge_id vía proj_id.
    queries_mov = {
        "stg_rgd_manifests": """
            SELECT dmwa.dmwa_id,
                   hwgr.hwge_id,
                   dmwa.dema_id as hwma_id,
                   dmwa.dmwa_quantity_tons as dmwa_waste_amount_generated,
                   dmwa.dmwa_date_create as dmwa_date_generated,
                   dmwa.dmwa_status,
                   'RETCE' as source_system
            FROM retce.detail_manifests_waste dmwa
            LEFT JOIN retce.detail_manifests dema ON dema.dema_id = dmwa.dema_id
            LEFT JOIN retce.hazardous_waste_generator_retce hwgr ON hwgr.hwgr_id = dema.tome_id
            WHERE dmwa.dmwa_quantity_tons > 0
        """
    }

    # 4. Consultas de Extracción - DOMINIO CUMPLIMIENTO (Declaraciones)
    queries_comp = {
    }

    try:
        # Ejecutar Ingestas por Dominio
        for domain_name, queryset in [("CORE", queries_core), ("GEO", queries_geo), 
                                      ("MOV", queries_mov)]:
            logger.info(f"[RGD_V2] -> Procesando Dominio: {domain_name}")
            for table_name, query in queryset.items():
                logger.info(f"   - Extrayendo {table_name}...")
                df = pd.read_sql(query, engine_suia)
                df.columns = [c.lower() for c in df.columns]
                
                # Carga a STG
                df.to_sql(table_name, engine_destino, schema='stg', if_exists='replace', index=False)
                logger.info(f"   - {len(df)} filas cargadas en stg.{table_name}")

        logger.info("[RGD_V2] Ingesta v2.0.0 finalizada exitosamente.")
        return True

    except Exception as e:
        logger.error(f"[RGD_ERROR] Error en ingesta v2.0.0: {e}")
        raise

if __name__ == "__main__":
    ejecutar_ingesta_waste_chemical()
