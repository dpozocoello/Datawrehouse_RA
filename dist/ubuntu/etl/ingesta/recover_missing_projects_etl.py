# ==============================================================================
# recover_missing_projects_etl.py — Recuperación de proyectos faltantes (v1.9.1)
# ==============================================================================
# Detecta proyectos presentes en stg.stg_intersection pero ausentes en
# dw.dim_proyecto, y los recupera de producción (coa_mae.project_licencing_coa).
#
# Esto previene que el UPSERT de dim_intersection falle silenciosamente 
# por falta de sk_proyecto correspondiente en dim_proyecto.
#
# Integrado como Paso 27 del pipeline ETL.
# ==============================================================================

import sys
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from sqlalchemy import create_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_SUIA_ENLISY, CONN_DWH_LOCAL
from utils import medir_tiempo, get_logger

logger = get_logger(__name__)


@medir_tiempo("RECOVER_MISSING_PROJECTS")
def ejecutar_recovery_proyectos() -> int:
    """
    Detecta proyectos en stg_intersection sin correspondencia en dim_proyecto
    y los recupera de producción.
    
    Returns:
        int: Número de proyectos recuperados.
    """
    try:
        # 1. Identificar proyectos faltantes
        logger.info("Identificando proyectos faltantes en dim_proyecto...")
        conn_dwh = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'], port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'], user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur_dwh = conn_dwh.cursor()
        cur_dwh.execute("""
            SELECT DISTINCT stg.project_code
            FROM stg.stg_intersection stg
            LEFT JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
            WHERE dp.sk_proyecto IS NULL
        """)
        missing_codes = [row[0] for row in cur_dwh.fetchall()]
        conn_dwh.close()

        if not missing_codes:
            logger.info("No hay proyectos faltantes. dim_proyecto está completo.")
            return 0

        logger.info(f"Detectados {len(missing_codes)} proyectos faltantes. Recuperando de producción...")

        # 2. Extraer datos mínimos de producción
        uri_suia = f"postgresql+psycopg2://{CONN_SUIA_ENLISY['user']}:{CONN_SUIA_ENLISY['password']}@{CONN_SUIA_ENLISY['host']}:{CONN_SUIA_ENLISY['port']}/{CONN_SUIA_ENLISY['database']}"
        engine_suia = create_engine(uri_suia)
        recovered_data = []
        batch_size = 5000
        with engine_suia.connect() as conn:
            for i in range(0, len(missing_codes), batch_size):
                batch = missing_codes[i:i+batch_size]
                df_temp = pd.read_sql_query(
                    "SELECT prco_cua AS codigo_proyecto, prco_name AS nombre_proyecto, "
                    "prco_description AS resumen_proyecto, "
                    "'SUIA-INTERSECTION-RECOVERY' AS sistema "
                    "FROM coa_mae.project_licencing_coa WHERE prco_cua IN %s",
                    conn, params=(tuple(batch),)
                )
                recovered_data.append(df_temp)
        
        df_recovered = pd.concat(recovered_data) if recovered_data else pd.DataFrame()
        engine_suia.dispose()

        if df_recovered.empty:
            logger.warning("No se encontraron datos en producción para los proyectos faltantes.")
            return 0

        logger.info(f"Recuperados {len(df_recovered)} proyectos de producción. Insertando en dim_proyecto...")

        # 3. Insertar en dw.dim_proyecto (ON CONFLICT DO NOTHING)
        conn_dwh = psycopg2.connect(
            host=CONN_DWH_LOCAL['host'], port=CONN_DWH_LOCAL['port'],
            database=CONN_DWH_LOCAL['database'], user=CONN_DWH_LOCAL['user'],
            password=CONN_DWH_LOCAL['password']
        )
        cur = conn_dwh.cursor()
        
        insert_sql = """
            INSERT INTO dw.dim_proyecto (codigo_proyecto, nombre_proyecto, resumen_proyecto, sistema) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT (codigo_proyecto) DO NOTHING
        """
        data = [
            (row['codigo_proyecto'], row['nombre_proyecto'], 
             row['resumen_proyecto'], row['sistema'])
            for _, row in df_recovered.iterrows()
        ]
        execute_batch(cur, insert_sql, data)
        conn_dwh.commit()
        conn_dwh.close()

        logger.info(f"[OK] {len(data)} proyectos recuperados e insertados en dim_proyecto.")
        return len(data)

    except Exception as e:
        logger.error(f"[RECOVER_MISSING_PROJECTS_ERROR] = {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    ejecutar_recovery_proyectos()
