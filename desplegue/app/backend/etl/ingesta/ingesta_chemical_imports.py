# ==============================================================================
# ingesta_chemical_imports.py - Ingesta de Registro de Importaciones a STG
# ==============================================================================
# Host SUIA: 172.16.0.179 | Host DWH: 172.16.0.226
# ==============================================================================

import pandas as pd
from sqlalchemy import create_engine
import sys
import os
import warnings

# Silenciar FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY, CONN_DWH_LOCAL
from utils import medir_tiempo, get_logger

logger = get_logger(__name__)

def build_uri(conn_dict):
    return f"postgresql://{conn_dict['user']}:{conn_dict['password']}@{conn_dict['host']}:{conn_dict['port']}/{conn_dict['database']}"

engine_suia = create_engine(build_uri(CONN_SUIA_ENLISY))
engine_destino = create_engine(build_uri(CONN_DWH_LOCAL))

print(f"DEBUG: Destination Engine URI: {build_uri(CONN_DWH_LOCAL)}")

@medir_tiempo("INGESTA_CHEMICAL_IMPORTS")
def ejecutar_ingesta_chemical_imports():
    logger.info("[INGESTA_CHEMICAL_IMPORTS] Iniciando extracción de importaciones...")

    queries_suia = {
        "stg_chemical_sustances_records": """
            SELECT chsr_id, prco_id, chsr_identification_rep_legal, chsr_name_rep_legal,
                   chsr_substance_registration, chsr_code, chsr_valid_since, chsr_valid_until, chsr_status
            FROM coa_chemical_sustances.chemical_sustances_records
        """,
        "stg_import_request": """
            SELECT inre_id, chsr_id, mach_id, dach_id, inre_authorization,
                   inre_begin_authorization_date, inre_end_authorization_date,
                   inre_processing_code, inre_document_autorizes, req_no, inre_type, inre_status
            FROM coa_chemical_sustances.import_request
        """,
        "stg_detail_import_request": """
            SELECT deir_id, inre_id, deir_available_space, deir_net_weight, deir_gross_weight, gelo_id, achs_id
            FROM coa_chemical_sustances.detail_import_request
        """,
        "stg_chemical_substances_declaration": """
            SELECT * FROM coa_chemical_sustances.chemical_substances_declaration
        """,
        "stg_chemical_substances_movements": """
            SELECT * FROM coa_chemical_sustances.chemical_substances_movements
        """,
        "stg_project_mapping": """
            SELECT prco_id, prco_cua FROM coa_mae.project_licencing_coa
        """
    }

    for table_name, query in queries_suia.items():
        try:
            logger.info(f"Extrayendo {table_name}...")
            df = pd.read_sql(query, engine_suia)
            print(f"DEBUG: {table_name} shape: {df.shape}")
            
            if not df.empty:
                logger.info(f"Cargando {len(df)} registros en stg.{table_name}...")
                df.to_sql(table_name, engine_destino, schema="stg", if_exists="replace", index=False)
            else:
                logger.warning(f"La tabla {table_name} está vacía en origen.")
                
        except Exception as e:
            logger.error(f"Error procesando {table_name}: {str(e)}")

    logger.info("[INGESTA_CHEMICAL_IMPORTS] Finalizado.")

if __name__ == "__main__":
    ejecutar_ingesta_chemical_imports()
