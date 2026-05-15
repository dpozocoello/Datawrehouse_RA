# ==============================================================================
# ingesta_all.py — Módulo unificado de las 9 transformaciones de ingesta
# ==============================================================================
# Cada función ejecuta una transformación de extracción desde un origen
# remoto hacia una tabla staging del Data Warehouse local.
#
# Patrón: TRUNCATE tabla_destino → SELECT origen → INSERT BATCH → COMMIT
#
# Equivalencias con Pentaho:
#   ejecutar_trx_01() ↔ TRX_01_INGESTA_SUIA_RCOA.ktr
#   ejecutar_trx_02() ↔ TRX_02_INGESTA_SUIA_COA.ktr
#   ...
#   ejecutar_trx_09() ↔ TRX_09_INGESTA_PAGOS_HIST.ktr
#   ejecutar_trx_10() ↔ TRX_10_INGESTA_AREAS.ktr
#   ejecutar_trx_11() ↔ TRX_11_GEOGRAFIA.ktr
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    CONN_SUIA_ENLISY, CONN_SUIA_BPMS, CONN_JBPM, CONN_JBPM_OLD,
    CONN_DWH_LOCAL, BATCH_SIZE
)
from connections import extract_to_staging
from utils import medir_tiempo, get_logger

logger = get_logger(__name__)


# ==============================================================================
# TRX_01: Ingesta SUIA RCOA
# ==============================================================================
# Origen: suia_enlisy → coa_mae.tmp_rcoa_bi
# Destino: stg.suia_rcoa_bi
# Descripción: Extrae proyectos del sistema RCOA (Registro de Control
#   Ambiental - Código Orgánico del Ambiente). Contiene 36 columnas con
#   datos de proyecto, proponente, ubicación geográfica, proceso/tarea,
#   resoluciones y áreas protegidas.
# ==============================================================================
QUERY_TRX_01 = """
SELECT
    "CÓDIGO PROYECTO"               AS codigo_proyecto,
    "NOMBRE PROYECTO"               AS nombre_proyecto,
    "RESUMEN PROYECTO"              AS resumen_proyecto,
    "DIRECCIÓN PROYECTO"            AS direccion_proyecto,
    "FECHA REGISTRO"                AS fecha_registro,
    "CÓDIGO ACTIVIDAD"              AS codigo_actividad,
    "ACTIVIDAD ECONÓMICA"           AS actividad_economica,
    "CED/RUC PROPONENTE"            AS ced_ruc_proponente,
    "NOMBRE PROPONENTE"             AS nombre_proponente,
    "ÁREA RESPONSABLE PROYECTO"     AS area_responsable_proyecto,
    "TIPO SECTOR"                   AS tipo_sector,
    "TIPO PERMISO AMBIENTAL"        AS tipo_permiso_ambiental,
    "TIPO ENTE"                     AS tipo_ente,
    "PROVINCIA"                     AS provincia,
    "CANTON"                        AS canton,
    "PARROQUIA"                     AS parroquia,
    "PROCESO"                       AS proceso,
    "ESTADO PROCESO"                AS estado_proceso,
    "FECHA INICIO PROCESO"::timestamp AS fecha_inicio_proceso,
    "FECHA FIN PROCESO"::timestamp  AS fecha_fin_proceso,
    "TAREA"                         AS tarea,
    "ESTADO TAREA"                  AS estado_tarea,
    "FECHA INICIO TAREA"            AS fecha_inicio_tarea,
    "FECHA FIN TAREA"               AS fecha_fin_tarea,
    "USUARIO TAREA"                 AS usuario_tarea,
    "ESTADO PROYECTO"               AS estado_proyecto,
    "INTERSECTA CON"                AS intersecta_con,
    "AREAS PROTEGIDAS"              AS areas_protegidas,
    "SISTEMA"                       AS sistema,
    "NOMBRE ZONA"                   AS nombre_zona,
    "FINALIZADO CON RESOLUCION"     AS finalizado_con_resolucion,
    "NUMERO RESOLUCION"             AS numero_resolucion,
    "FECHA RESOLUCION"              AS fecha_resolucion,
    "ID AREA"                       AS id_area,
    "ESTADO TRÁMITE"                AS estado_tramite,
    "SUPERFICIE PROYECTO"           AS superficie_proyecto
FROM coa_mae.tmp_rcoa_bi
"""

@medir_tiempo("TRX_01_SUIA_RCOA")
def ejecutar_trx_01() -> int:
    """Extrae datos RCOA de suia_enlisy y carga en stg.suia_rcoa_bi."""
    return extract_to_staging(
        origen_params=CONN_SUIA_ENLISY,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_01,
        tabla_destino="stg.suia_rcoa_bi",
        paso_nombre="TRX_01_SUIA_RCOA",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_02: Ingesta SUIA COA
# ==============================================================================
# Origen: suia_enlisy → suia_iii.tmp_coa_bi
# Destino: stg.suia_coa_bi
# Descripción: Extrae proyectos del sistema COA (Código Orgánico del Ambiente,
#   versión anterior). Misma estructura de 36 columnas que TRX_01 pero desde
#   el esquema suia_iii en vez de coa_mae.
# ==============================================================================
QUERY_TRX_02 = """
SELECT
    "CÓDIGO PROYECTO"               AS codigo_proyecto,
    "NOMBRE PROYECTO"               AS nombre_proyecto,
    "RESUMEN PROYECTO"              AS resumen_proyecto,
    "DIRECCIÓN PROYECTO"            AS direccion_proyecto,
    "FECHA REGISTRO"                AS fecha_registro,
    "CÓDIGO ACTIVIDAD"              AS codigo_actividad,
    "ACTIVIDAD ECONÓMICA"           AS actividad_economica,
    "CED/RUC PROPONENTE"            AS ced_ruc_proponente,
    "NOMBRE PROPONENTE"             AS nombre_proponente,
    "ÁREA RESPONSABLE PROYECTO"     AS area_responsable_proyecto,
    "TIPO SECTOR"                   AS tipo_sector,
    "TIPO PERMISO AMBIENTAL"        AS tipo_permiso_ambiental,
    "TIPO ENTE"                     AS tipo_ente,
    "PROVINCIA"                     AS provincia,
    "CANTON"                        AS canton,
    "PARROQUIA"                     AS parroquia,
    "PROCESO"                       AS proceso,
    "ESTADO PROCESO"                AS estado_proceso,
    "FECHA INICIO PROCESO"::timestamp AS fecha_inicio_proceso,
    "FECHA FIN PROCESO"::timestamp  AS fecha_fin_proceso,
    "TAREA"                         AS tarea,
    "ESTADO TAREA"                  AS estado_tarea,
    "FECHA INICIO TAREA"            AS fecha_inicio_tarea,
    "FECHA FIN TAREA"               AS fecha_fin_tarea,
    "USUARIO TAREA"                 AS usuario_tarea,
    "ESTADO PROYECTO"               AS estado_proyecto,
    "INTERSECTA CON"                AS intersecta_con,
    "AREAS PROTEGIDAS"              AS areas_protegidas,
    "SISTEMA"                       AS sistema,
    "NOMBRE ZONA"                   AS nombre_zona,
    "FINALIZADO CON RESOLUCION"     AS finalizado_con_resolucion,
    "NUMERO RESOLUCION"             AS numero_resolucion,
    "FECHA RESOLUCION"              AS fecha_resolucion,
    "ID AREA"                       AS id_area,
    "ESTADO TRÁMITE"                AS estado_tramite,
    "SUPERFICIE PROYECTO"           AS superficie_proyecto
FROM suia_iii.tmp_coa_bi
"""

@medir_tiempo("TRX_02_SUIA_COA")
def ejecutar_trx_02() -> int:
    """Extrae datos COA de suia_enlisy y carga en stg.suia_coa_bi."""
    return extract_to_staging(
        origen_params=CONN_SUIA_ENLISY,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_02,
        tabla_destino="stg.suia_coa_bi",
        paso_nombre="TRX_02_SUIA_COA",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_03: Ingesta JBPM Sector / Subsector
# ==============================================================================
# Origen: jbpmdb_prod_old → public.vm_sector_subsector_bi
# Destino: stg.jbpm_sector_bi
# Descripción: Extrae proyectos del motor jBPM legacy organizados por
#   sector y subsector económico. Incluye campos propios como
#   ente_acreditado y estratégico (no presentes en fuentes SUIA).
# ==============================================================================
QUERY_TRX_03 = """
SELECT
    "CÓDIGO PROYECTO"               AS codigo_proyecto,
    "NOMBRE PROYECTO"               AS nombre_proyecto,
    "RESUMEN PROYECTO"              AS resumen_proyecto,
    "DIRECCIÓN PROYECTO"            AS direccion_proyecto,
    "FECHA REGISTRO"                AS fecha_registro,
    "CÓDIGO ACTIVIDAD"              AS codigo_actividad,
    "ACTIVIDAD ECONÓMICA"           AS actividad_economica,
    "CED/RUC PROPONENTE"            AS ced_ruc_proponente,
    "NOMBRE PROPONENTE"             AS nombre_proponente,
    "ÁREA RESPONSABLE PROYECTO"     AS area_responsable_proyecto,
    "TIPO SECTOR"                   AS tipo_sector,
    "TIPO PERMISO AMBIENTAL"        AS tipo_permiso_ambiental,
    "TIPO ENTE"                     AS tipo_ente,
    "PROVINCIA"                     AS provincia,
    "CANTON"                        AS canton,
    "PARROQUIA"                     AS parroquia,
    "PROCESO"                       AS proceso,
    "ESTADO PROCESO"                AS estado_proceso,
    "FECHA INICIO PROCESO"::timestamp AS fecha_inicio_proceso,
    "FECHA FIN PROCESO"::timestamp  AS fecha_fin_proceso,
    "TAREA"                         AS tarea,
    "ESTADO TAREA"                  AS estado_tarea,
    "FECHA INICIO TAREA"            AS fecha_inicio_tarea,
    "FECHA FIN TAREA"               AS fecha_fin_tarea,
    "USUARIO TAREA"                 AS usuario_tarea,
    "ESTADO PROYECTO"               AS estado_proyecto,
    "INTERSECTA CON"                AS intersecta_con,
    "AREAS PROTEGIDAS"::text        AS areas_protegidas,
    "SISTEMA"                       AS sistema,
    "ENTE ACREDITADO"               AS ente_acreditado,
    "ESTADO TRÁMITE"                AS estado_tramite,
    "ESTRATÉGICO"                   AS estrategico
FROM public.vm_sector_subsector_bi
"""

@medir_tiempo("TRX_03_JBPM_SECTOR")
def ejecutar_trx_03() -> int:
    """Extrae datos de Sector/Subsector desde jbpmdb_prod_old y carga en stg.jbpm_sector_bi."""
    return extract_to_staging(
        origen_params=CONN_JBPM_OLD,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_03,
        tabla_destino="stg.jbpm_sector_bi",
        paso_nombre="TRX_03_JBPM_SECTOR",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_04: Ingesta JBPM 4 Categorías
# ==============================================================================
# Origen: jbpmdb → public.vm_cuatro_categorias_bi
# Destino: stg.jbpm_4cat_bi
# Descripción: Extrae proyectos clasificados en las 4 categorías de
#   impacto ambiental desde el motor jBPM actual.
# ==============================================================================
QUERY_TRX_04 = """
SELECT
    "CÓDIGO PROYECTO"               AS codigo_proyecto,
    "NOMBRE PROYECTO"               AS nombre_proyecto,
    "RESUMEN PROYECTO"              AS resumen_proyecto,
    "DIRECCIÓN PROYECTO"            AS direccion_proyecto,
    "FECHA REGISTRO"                AS fecha_registro,
    "CÓDIGO ACTIVIDAD"              AS codigo_actividad,
    "ACTIVIDAD ECONÓMICA"           AS actividad_economica,
    "CED/RUC PROPONENTE"            AS ced_ruc_proponente,
    "NOMBRE PROPONENTE"             AS nombre_proponente,
    "ÁREA RESPONSABLE PROYECTO"     AS area_responsable_proyecto,
    "TIPO SECTOR"                   AS tipo_sector,
    "TIPO PERMISO AMBIENTAL"        AS tipo_permiso_ambiental,
    "TIPO ENTE"                     AS tipo_ente,
    "PROVINCIA"                     AS provincia,
    "CANTON"                        AS canton,
    "PARROQUIA"                     AS parroquia,
    "PROCESO"                       AS proceso,
    "ESTADO PROCESO"                AS estado_proceso,
    "FECHA INICIO PROCESO"          AS fecha_inicio_proceso,
    "FECHA FIN PROCESO"             AS fecha_fin_proceso,
    "TAREA"                         AS tarea,
    "ESTADO TAREA"                  AS estado_tarea,
    "FECHA INICIO TAREA"            AS fecha_inicio_tarea,
    "FECHA FIN TAREA"               AS fecha_fin_tarea,
    "USUARIO TAREA"                 AS usuario_tarea,
    "ESTADO PROYECTO"               AS estado_proyecto,
    "INTERSECTA CON"                AS intersecta_con,
    "AREAS PROTEGIDAS"              AS areas_protegidas,
    "SISTEMA"                       AS sistema,
    "ENTE ACREDITADO"               AS ente_acreditado,
    "ESTADO TRÁMITE"                AS estado_tramite,
    "ESTRATÉGICO"                   AS estrategico
FROM public.vm_cuatro_categorias_bi
"""

@medir_tiempo("TRX_04_JBPM_4CAT")
def ejecutar_trx_04() -> int:
    """Extrae datos de 4 Categorías desde jbpmdb y carga en stg.jbpm_4cat_bi."""
    return extract_to_staging(
        origen_params=CONN_JBPM,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_04,
        tabla_destino="stg.jbpm_4cat_bi",
        paso_nombre="TRX_04_JBPM_4CAT",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_05: Ingesta JBPM Hidrocarburos (DESHABILITADO)
# ==============================================================================
# Origen: jbpmdb → public.vwt_hidrocarbonos_bi
# Destino: stg.jbpm_hidro_bi
# Descripción: Extrae proyectos de hidrocarburos con Licencia Ambiental.
#   NOTA: Este paso está deshabilitado en la configuración actual de Pentaho.
# ==============================================================================
QUERY_TRX_05 = """
SELECT
    "CÓDIGO PROYECTO"               AS codigo_proyecto,
    "NOMBRE PROYECTO"               AS nombre_proyecto,
    "RESUMEN" AS resumen_proyecto,
    "DIRECCIÓN PROYECTO"            AS direccion_proyecto,
    "FECHA REGISTRO"                AS fecha_registro,
    "CÓDIGO ACTIVIDAD"              AS codigo_actividad,
    "ACTIVIDAD ECONÓMICA"           AS actividad_economica,
    "CED/RUC EMPRESA"               AS ced_ruc_proponente,
    "NOMBRE EMPRESA"                AS nombre_proponente,
    "ÁREA RESPONSABLE PROYECTO"     AS area_responsable_proyecto,
    "TIPO SECTOR"                   AS tipo_sector,
    'Licencia Ambiental'            AS tipo_permiso_ambiental,
    "TIPO ENTE"                     AS tipo_ente,
    "PROVINCIA"                     AS provincia,
    "CANTÓN"                        AS canton,
    "PARROQUIA"                     AS parroquia,
    "PROCESO"                       AS proceso,
    "ESTADO PROCESO"                AS estado_proceso,
    "FECHA INICIO PROCESO"          AS fecha_inicio_proceso,
    "FECHA FIN PROCESO"             AS fecha_fin_proceso,
    "TAREA"                         AS tarea,
    "ESTADO TAREA"                  AS estado_tarea,
    "FECHA INICIO TAREA"            AS fecha_inicio_tarea,
    "FECHA FIN TAREA"               AS fecha_fin_tarea,
    "USUARIO TAREA"                 AS usuario_tarea,
    "ESTADO PROYECTO"               AS estado_proyecto,
    "INTERSECTA CON"                AS intersecta_con,
    "ID AREA"                       AS id_area,
    "ENTE ACREDITADO"               AS ente_acreditado,
    "ESTADO TRÁMITE"                AS estado_tramite
FROM public.vwt_hidrocarbonos_bi
"""

@medir_tiempo("TRX_05_JBPM_HIDRO")
def ejecutar_trx_05() -> int:
    """Extrae datos de Hidrocarburos desde jbpmdb y carga en stg.jbpm_hidro_bi."""
    return extract_to_staging(
        origen_params=CONN_JBPM,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_05,
        tabla_destino="stg.jbpm_hidro_bi",
        paso_nombre="TRX_05_JBPM_HIDRO",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_06: Ingesta Variables SNAP
# ==============================================================================
# Origen: suia_bpms_enlisy_app → variableinstancelog + processinstancelog
# Destino: stg.jbpm_snap_variables
# Descripción: Identifica procesos BPM que tienen una variable SNAP activa.
#   Esto permite determinar qué proyectos pasan por el Sistema Nacional
#   de Áreas Protegidas (SNAP), lo cual se refleja en el campo
#   interseccion_snap de la fact table.
# ==============================================================================
QUERY_TRX_06 = """
SELECT DISTINCT
    v.value                AS codigo_proyecto,
    p.processinstanceid    AS processinstanceid,
    p.processname          AS nombre_proceso,
    p.status               AS estado_proceso,
    p.start_date           AS fecha_inicio_proceso,
    p.end_date             AS fecha_fin_proceso
FROM variableinstancelog v
    LEFT JOIN processinstancelog p ON p.processinstanceid = v.processinstanceid
WHERE v.variableid IN ('tramite', 'numero_tramite')
    AND p.status IN (1, 2)
    AND EXISTS (
        SELECT 1
        FROM variableinstancelog snap
        WHERE snap.processinstanceid = p.processinstanceid
          AND snap.variableid ILIKE '%snap%'
    )
"""

@medir_tiempo("TRX_06_SNAP")
def ejecutar_trx_06() -> int:
    """Extrae variables SNAP del BPM y carga en stg.jbpm_snap_variables."""
    return extract_to_staging(
        origen_params=CONN_SUIA_BPMS,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_06,
        tabla_destino="stg.jbpm_snap_variables",
        paso_nombre="TRX_06_SNAP",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_07: Ingesta Pagos JBPM
# ==============================================================================
# Origen: jbpmdb → online_payment.online_payments_historical
#                  JOIN online_payment.online_payments
# Destino: stg.online_payments_bi
# Descripción: Extrae pagos en línea realizados a través del sistema jBPM.
#   Solo incluye transacciones con estado exitoso (transaction_state = true).
#   El JOIN con online_payments obtiene los datos financieros de cada pago.
# ==============================================================================
QUERY_TRX_07 = """
SELECT
    p.id_online_payment    AS online_payment_id,
    h.project_id           AS project_id,
    h.tramit_number        AS tramit_number,
    p.convenience_number   AS convenience_number,
    p.bank_code            AS bank_code,
    p.payment_value::numeric(12,2) AS payment_value,
    p.date_hour_transaction::timestamp AS date_hour_transaction,
    p.transaction_type     AS transaction_type,
    p.transaction_state    AS transaction_state
FROM online_payment.online_payments_historical h
    JOIN online_payment.online_payments p
        ON h.online_payment_id = p.id_online_payment
WHERE p.transaction_state = true
"""

@medir_tiempo("TRX_07_PAGOS_JBPM")
def ejecutar_trx_07() -> int:
    """Extrae pagos JBPM online y carga en stg.online_payments_bi."""
    return extract_to_staging(
        origen_params=CONN_JBPM,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_07,
        tabla_destino="stg.online_payments_bi",
        paso_nombre="TRX_07_PAGOS_JBPM",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_08: Ingesta Pagos SUIA
# ==============================================================================
# Origen: suia_enlisy → suia_iii.financial_transaction
#                        JOIN coa_mae.project_licencing_coa
#                        JOIN suia_iii.financial_transaction_log
# Destino: stg.financial_transaction_bi
# Descripción: Extrae transacciones financieras del sistema SUIA.
#   El JOIN con project_licencing_coa vincula la transacción con el
#   código de proyecto. El JOIN con financial_transaction_log obtiene
#   el nombre de la tarea y proceso BPM asociados.
# ==============================================================================
QUERY_TRX_08 = """
SELECT DISTINCT
    ft.fitr_id                    AS fitr_id,
    plc.prco_cua                  AS codigo_proyecto,
    ft.fitr_transaction_amount    AS fitr_transaction_amount,
    ft.fitr_paid_value            AS fitr_paid_value,
    ft.fitr_transaction_number    AS fitr_transaction_number,
    ft.fitr_payment_type          AS fitr_payment_type,
    CASE ft.fitr_payment_type
        WHEN 1 THEN 'Pago Licencia'
        WHEN 2 THEN 'Pago Inventario'
        WHEN 3 THEN 'Pago RGD'
        ELSE 'Otro Pago'
    END                           AS payment_type_desc,
    ft.fitr_creation_date         AS fitr_creation_date,
    ft.fitr_status                AS fitr_status,
    ftl.task_name                 AS task_name,
    ftl.processname               AS processname,
    ftl.processinstanceid         AS processinstanceid
FROM suia_iii.financial_transaction ft
    LEFT JOIN coa_mae.project_licencing_coa plc
        ON ft.prco_id = plc.prco_id
    LEFT JOIN suia_iii.financial_transaction_log ftl
        ON ft.fitr_id = ftl.fitr_id
WHERE ft.fitr_status = true
"""

@medir_tiempo("TRX_08_PAGOS_SUIA")
def ejecutar_trx_08() -> int:
    """Extrae transacciones financieras SUIA y carga en stg.financial_transaction_bi."""
    return extract_to_staging(
        origen_params=CONN_SUIA_ENLISY,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_08,
        tabla_destino="stg.financial_transaction_bi",
        paso_nombre="TRX_08_PAGOS_SUIA",
        batch_size=BATCH_SIZE
    )


# ==============================================================================
# TRX_09: Ingesta Pagos Históricos JBPM (v3)
# ==============================================================================
# Origen: jbpmdb → online_payment.online_payments_historical
# Destino: stg.online_payments_historical_bi
# Descripción: Extrae el historial completo de movimientos de pagos en línea.
#   Estos datos permiten recalcular el monto real de cada transacción
#   basándose en el saldo remanente (value_updated) y el valor retirado
#   (retired_value). Este paso se agregó en la versión v3 del ETL.
# ==============================================================================
QUERY_TRX_09 = """
SELECT
    id_online_payment_historical,
    description,
    project_id,
    retired_value,
    sender_ip,
    tramit_number,
    update_date,
    value_updated,
    online_payment_id,
    enabled,
    user_create,
    user_modification,
    date_create,
    date_modification,
    reactivate,
    observations,
    retired_value_1
FROM online_payment.online_payments_historical
"""

@medir_tiempo("TRX_09_PAGOS_HIST")
def ejecutar_trx_09() -> int:
    """Extrae historial de pagos JBPM y carga en stg.online_payments_historical_bi."""
    return extract_to_staging(
        origen_params=CONN_JBPM,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_09,
        tabla_destino="stg.online_payments_historical_bi",
        paso_nombre="TRX_09_PAGOS_HIST",
        batch_size=BATCH_SIZE
    )

# ==============================================================================
# TRX_10: Ingesta Areas (Oficinas Técnicas)
# ==============================================================================
# Origen: suia_enlisy → public.areas
# Destino: stg.suia_areas_bi
# Descripción: Extrae el catálogo de áreas (oficinas técnicas, zonas, etc.)
#   del sistema SUIA para permitir dimensiones de análisis geográfico/admin.
# ==============================================================================
QUERY_TRX_10 = """
SELECT
    area_id,
    area_name,
    area_abbreviation,
    area_parent_id,
    zone_id,
    gelo_id, -- [v1.2]
    area_status,
    area_campus,
    arty_id
FROM public.areas
"""

@medir_tiempo("TRX_10_AREAS")
def ejecutar_trx_10() -> int:
    """Extrae datos de Areas desde suia_enlisy y carga en stg.suia_areas_bi."""
    return extract_to_staging(
        origen_params=CONN_SUIA_ENLISY,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_10,
        tabla_destino="stg.suia_areas_bi",
        paso_nombre="TRX_10_AREAS",
        batch_size=BATCH_SIZE
    )

# ==============================================================================
# TRX_11: Ingesta Catalogo Geográfico (v1.2)
# ==============================================================================
# Origen: suia_enlisy → public.geographical_locations
# Destino: stg.geographical_locations_bi
# Descripción: Extrae el catálogo completo de Provincias, Cantones y Parroquias.
# ==============================================================================
QUERY_TRX_11 = """
SELECT
    gelo_id,
    gelo_name,
    gelo_parent_id,
    gelo_codification_inec
FROM public.geographical_locations
"""

@medir_tiempo("TRX_11_GEOGRAFIA")
def ejecutar_trx_11() -> int:
    """Extrae datos de Geografía desde suia_enlisy y carga en stg.geographical_locations_bi."""
    return extract_to_staging(
        origen_params=CONN_SUIA_ENLISY,
        destino_params=CONN_DWH_LOCAL,
        query_origen=QUERY_TRX_11,
        tabla_destino="stg.geographical_locations_bi",
        paso_nombre="TRX_11_GEOGRAFIA",
        batch_size=BATCH_SIZE
    )
