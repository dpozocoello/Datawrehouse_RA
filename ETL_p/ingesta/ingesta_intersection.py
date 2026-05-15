# ==============================================================================
# ingesta_intersection.py - Ingesta Mejorada de Intersecciones (v1.9.1)
# ==============================================================================
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import sys
import os

# Configuración de rutas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY, CONN_SUIA_BPMS, CONN_DWH_LOCAL, PROJECT_ROOT
from utils import medir_tiempo, get_logger

logger = get_logger(__name__)

# Mapeos de Capas Identificados en Auditoría (Corregido v1.9.1)
SNAP_IDS = {1, 11, 21}
BOSQUE_IDS = {2, 3, 26, 41} # v1.9.1: Se añade ID 2 (Area de Bosque y Veg. Protectora)
PATRIMONIO_IDS = {27, 31}
INTANGIBLE_IDS = {28, 51}

@medir_tiempo("INGESTA_INTERSECTION")
def ejecutar_ingesta_intersection_v2():
    logger.info("[INGESTA_INTERSECTION] Iniciando proceso de ingesta mejorada...")
    
    try:
        # 1. Extraer Intersecciones desde SUIA (coa_mae)
        logger.info("Extraer capas geográficas desde coa_mae (179)...")
        uri_suia = f"postgresql+psycopg2://{CONN_SUIA_ENLISY['user']}:{CONN_SUIA_ENLISY['password']}@{CONN_SUIA_ENLISY['host']}:{CONN_SUIA_ENLISY['port']}/{CONN_SUIA_ENLISY['database']}"
        engine_suia = create_engine(uri_suia)
        query_suia = """
            SELECT 
                iplc.laye_id, 
                plc.prco_cua as project_code,
                cic.prco_id,
                cic.cein_code as certificate_code,
                cic.cein_creation_date as certificate_date,
                cic.cein_location as html_location,
                cic.cein_layers as html_layers,
                cic.cein_other_intersection as ecosystems
            FROM coa_mae.certificate_intersection_coa cic
            JOIN coa_mae.project_licencing_coa plc ON cic.prco_id = plc.prco_id
            LEFT JOIN coa_mae.intersections_project_licencing_coa iplc ON cic.prco_id = iplc.prco_id AND iplc.inpr_status = TRUE
            WHERE cic.cein_status = TRUE
        """
        with engine_suia.connect() as conn:
            df_raw = pd.read_sql_query(query_suia, conn)
        engine_suia.dispose()
        
        # 2. Extraer Variables BPM (SNAP)
        logger.info("Extraer variables SNAP desde suia_bpms...")
        uri_bpms = f"postgresql+psycopg2://{CONN_SUIA_BPMS['user']}:{CONN_SUIA_BPMS['password']}@{CONN_SUIA_BPMS['host']}:{CONN_SUIA_BPMS['port']}/{CONN_SUIA_BPMS['database']}"
        engine_bpms = create_engine(uri_bpms)
        query_bpm = """
            SELECT DISTINCT v.value as project_code
            FROM variableinstancelog v
            JOIN bamtasksummary b ON v.processinstanceid = b.processinstanceid
            WHERE v.variableid ILIKE '%%snap%%' AND b.status = 'Completed'
        """
        with engine_bpms.connect() as conn:
            df_bpm_snap = pd.read_sql_query(query_bpm, conn)
        df_bpm_snap['has_bpm_snap'] = True
        engine_bpms.dispose()
        
        # 3. Consolidación y Lógica de Negocio
        logger.info("Consolidando información y construyendo dictámenes...")
        
        # Agrupar capas por proyecto
        df_grouped = df_raw.groupby([
            'project_code', 'prco_id', 'certificate_code', 'certificate_date', 
            'html_location', 'html_layers', 'ecosystems'
        ])['laye_id'].apply(list).reset_index()
        
        # Merge con variables BPM
        df_final = df_grouped.merge(df_bpm_snap, on='project_code', how='left').fillna(False).infer_objects(copy=False)
        
        def build_dictamen(row):
            lset = set(row['laye_id'])
            
            # SNAP
            is_snap = not lset.isdisjoint(SNAP_IDS) or row['has_bpm_snap']
            snap_text = "SI INTERSECA con el Sistema Nacional de Áreas Protegidas (SNAP)" if is_snap else "NO INTERSECA con el Sistema Nacional de Áreas Protegidas (SNAP)"
            
            # Otras capas
            others = []
            if not lset.isdisjoint(BOSQUE_IDS): others.append("BOSQUES PROTECTORES")
            if not lset.isdisjoint(PATRIMONIO_IDS): others.append("PATRIMONIO FORESTAL")
            if not lset.isdisjoint(INTANGIBLE_IDS): others.append("ZONAS INTANGIBLES")
            
            others_text = " e interseca con: " + ", ".join(others) if others else "."
            
            ecosystems = f"<br/>{row['ecosystems']}" if row['ecosystems'] else ""
            return f"<strong>{snap_text}</strong>{others_text}{ecosystems}"

        df_final['dictamen_final'] = df_final.apply(build_dictamen, axis=1)
        
        # Seleccionar columnas para el DWH
        output_cols = ['project_code', 'certificate_code', 'certificate_date', 'html_location', 'html_layers', 'dictamen_final']
        df_to_load = df_final[output_cols]
        
        # 4. Carga en Local
        logger.info(f"Cargando {len(df_to_load)} registros en stg.stg_intersection...")
        engine_local = create_engine(f"postgresql://{CONN_DWH_LOCAL['user']}:{CONN_DWH_LOCAL['password']}@{CONN_DWH_LOCAL['host']}:{CONN_DWH_LOCAL['port']}/{CONN_DWH_LOCAL['database']}")
        
        df_to_load.to_sql('stg_intersection', engine_local, schema='stg', if_exists='replace', index=False)
        logger.info("OK - Datos cargados en stg.stg_intersection")
        
    except Exception as e:
        logger.error(f"[INGESTA_INTERSECTION_ERROR] = {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    ejecutar_ingesta_intersection_v2()
