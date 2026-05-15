# ==============================================================================
# ingesta_pesticides.py - Ingesta de Registro de Plaguicidas a STG
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

@medir_tiempo("INGESTA_PESTICIDES")
def ejecutar_ingesta_pesticides():
    logger.info("[INGESTA_PESTICIDES] Iniciando extracción de plaguicidas...")

    queries_suia = {
        "stg_pesticide_project": """
            SELECT chpe_id, chpe_proyect_code, chpe_status
            FROM chemical_pesticides.pesticide_project
        """,
        "stg_products_pqa": """
            SELECT prod_id as pqa_id, prod_trade_name_product as pqa_name, 
                   prod_register_number as pqa_registration_number, 
                   prod_toxicological_category as pqa_toxicological_category
            FROM chemical_pesticides.products_pqa
        """,
        "stg_detail_pesticide_project": """
            SELECT depp_id, chpe_id, prod_id as pqa_id
            FROM chemical_pesticides.detail_pesticide_project
        """
    }

    for table_name, query in queries_suia.items():
        try:
            logger.info(f"Extrayendo {table_name}...")
            df = pd.read_sql(query, engine_suia)
            
            if not df.empty:
                logger.info(f"Cargando {len(df)} registros en stg.{table_name}...")
                df.to_sql(table_name, engine_destino, schema="stg", if_exists="replace", index=False)
            else:
                logger.warning(f"La tabla {table_name} está vacía en origen.")
                
        except Exception as e:
            logger.error(f"Error procesando {table_name}: {str(e)}")

    logger.info("[INGESTA_PESTICIDES] Finalizado.")

if __name__ == "__main__":
    ejecutar_ingesta_pesticides()
