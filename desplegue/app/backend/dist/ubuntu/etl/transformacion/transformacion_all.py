# ==============================================================================
# transformacion_all.py — Módulo unificado de los 9 pasos de transformación
# ==============================================================================
# Cada función ejecuta un Stored Procedure o sentencia SQL de transformación
# contra el Data Warehouse local (dw_reg_v1).
#
# Estos pasos se ejecutan DESPUÉS de las 9 ingestas y procesan los datos
# de staging para poblar las tablas dimensionales y de hechos.
#
# Orden de ejecución:
#   1. sp_consolidar_staging()    → Unifica staging en consolidado
#   2. sp_carga_dimensiones()     → Puebla las 7 dimensiones
#   3. sp_carga_hechos()          → Puebla fact_regularizacion
#   4. sp_carga_dim_pago()        → Puebla dim_pago
#   5. sp_carga_fact_pago()       → Puebla fact_pago
#   6. update_area_responsable()  → Actualiza área en dim_proyecto (v2)
#   7. sp_bridge_proyecto_geo()   → Puebla bridge proyecto-geografía (v2)
#   8. recalculo_montos_jbpm()    → Corrige montos con saldos históricos (v3)
#   9. sp_secuencia_pagos()       → Calcula secuencia y acumulado (v2/v3)
#   10. sp_carga_dim_area()      → Puebla dim_area (v1.1)
#   11. sp_orquestar_extraccion_remota() → Dispara SPs v1.4.1 en origen
#   12. sp_carga_puente_ambiental() → Puebla bridge table de biodiversidad
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONN_DWH_LOCAL
from connections import execute_sp, execute_sql
from utils import medir_tiempo, get_logger

logger = get_logger(__name__)


# ==============================================================================
# PASO 9: Consolidar Staging
# ==============================================================================
# Equivalente Pentaho: SP Consolidar Staging (entrada tipo SQL)
# Stored Procedure: dw.sp_consolidar_staging()
#
# Descripción:
#   Unifica las 5 tablas staging individuales (suia_rcoa_bi, suia_coa_bi,
#   jbpm_sector_bi, jbpm_4cat_bi, jbpm_hidro_bi) en una sola tabla
#   consolidada (stg.consolidado_proyectos) mediante UNION ALL.
#
#   Cada origen tiene columnas ligeramente diferentes; el SP normaliza
#   a un esquema uniforme de ~39 columnas, agregando la columna 'origen'
#   como discriminador de la fuente de datos.
#
# Dependencias:
#   - Requiere que TRX_01 a TRX_05 hayan completado exitosamente
#   - La tabla consolidado_proyectos se trunca antes de insertar
# ==============================================================================
@medir_tiempo("SP_CONSOLIDAR_STAGING")
def sp_consolidar_staging():
    """Ejecuta dw.sp_consolidar_staging() — UNION ALL de las 5 tablas staging."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_consolidar_staging()", "SP_CONSOLIDAR_STAGING")


# ==============================================================================
# PASO 10: Cargar Dimensiones
# ==============================================================================
# Equivalente Pentaho: SP Cargar Dimensiones (entrada tipo SQL)
# Stored Procedure: dw.sp_carga_dimensiones()
#
# Descripción:
#   Puebla las 7 tablas dimensionales del modelo estrella desde
#   stg.consolidado_proyectos. Usa INSERT ON CONFLICT para manejar
#   actualizaciones incrementales (upsert).
#
#   Dimensiones procesadas:
#     - dim_tiempo      → Rango de fechas 2005-2030
#     - dim_proyecto    → DISTINCT ON(codigo_proyecto) + ON CONFLICT DO UPDATE
#     - dim_proponente  → Por ced_ruc_proponente + ON CONFLICT DO UPDATE
#     - dim_actividad   → Por codigo_actividad + ON CONFLICT DO NOTHING
#     - dim_geografia   → Por (provincia, canton, parroquia) + ON CONFLICT DO NOTHING
#     - dim_usuario     → Por usuario_tarea + ON CONFLICT DO NOTHING
#     - dim_estado      → Por (estado_proceso, estado_proyecto) + ON CONFLICT DO NOTHING
#
# Dependencias:
#   - Requiere SP_CONSOLIDAR_STAGING completado
# ==============================================================================
@medir_tiempo("SP_CARGA_DIMENSIONES")
def sp_carga_dimensiones():
    """Ejecuta dw.sp_carga_dimensiones() — Puebla las 7 dimensiones del modelo estrella."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_carga_dimensiones()", "SP_CARGA_DIMENSIONES")


# ==============================================================================
# PASO 11: Cargar Tabla de Hechos (Regularización)
# ==============================================================================
# Equivalente Pentaho: SP Cargar Fact Table (entrada tipo SQL)
# Stored Procedure: dw.sp_carga_hechos()
#
# Descripción:
#   Puebla dw.fact_regularizacion realizando JOINs con todas las
#   dimensiones mediante claves naturales. También hace LEFT JOIN con
#   stg.jbpm_snap_variables para determinar si el proyecto intersecta
#   con el Sistema Nacional de Áreas Protegidas (SNAP).
#
#   La columna interseccion_snap se calcula como:
#     - 'SI' si el proyecto aparece en jbpm_snap_variables
#     - 'NO' en caso contrario
#
# Dependencias:
#   - Requiere SP_CARGA_DIMENSIONES completado
#   - Requiere TRX_06 (SNAP) para la intersección
# ==============================================================================
@medir_tiempo("SP_CARGA_HECHOS")
def sp_carga_hechos():
    """Ejecuta dw.sp_carga_hechos() — Puebla fact_regularizacion con intersección SNAP."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_carga_hechos()", "SP_CARGA_HECHOS")


# ==============================================================================
# PASO 12: Cargar Dimensión de Pago
# ==============================================================================
# Equivalente Pentaho: SP Cargar Dim Pago (entrada tipo SQL)
# Stored Procedure: dw.sp_carga_dim_pago()
#
# Descripción:
#   Puebla dw.dim_pago con los tipos de pago únicos desde dos fuentes:
#     - JBPM: tipo_pago='Online Payment', bank_code, transaction_type
#     - SUIA: tipo_pago=payment_type_desc (Pago Licencia, Inventario, RGD)
#
# Dependencias:
#   - Requiere TRX_07 y TRX_08 completados
# ==============================================================================
@medir_tiempo("SP_CARGA_DIM_PAGO")
def sp_carga_dim_pago():
    """Ejecuta dw.sp_carga_dim_pago() — Puebla dim_pago desde JBPM y SUIA."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_carga_dim_pago()", "SP_CARGA_DIM_PAGO")


# ==============================================================================
# PASO 13: Cargar Tabla de Hechos de Pagos
# ==============================================================================
# Equivalente Pentaho: SP Cargar Fact Pago (entrada tipo SQL)
# Stored Procedure: dw.sp_carga_fact_pago()
#
# Descripción:
#   Puebla dw.fact_pago con deduplicación mediante ON CONFLICT.
#   Procesa pagos en tres partes:
#     - Parte A: Pagos JBPM directos (por project_id)
#     - Parte B: Pagos JBPM indirectos (misma transacción, otro proyecto
#                del mismo proponente)
#     - Parte C: Pagos SUIA (financial_transaction)
#
# Dependencias:
#   - Requiere SP_CARGA_DIM_PAGO completado
#   - Requiere dim_proyecto poblada
# ==============================================================================
@medir_tiempo("SP_CARGA_FACT_PAGO")
def sp_carga_fact_pago():
    """Ejecuta dw.sp_carga_fact_pago() — Puebla fact_pago con deduplicación."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_carga_fact_pago()", "SP_CARGA_FACT_PAGO")


# ==============================================================================
# PASO 14: Actualizar Área Responsable (v2)
# ==============================================================================
# Equivalente Pentaho: Update Area Responsable (entrada tipo SQL)
#
# Descripción:
#   Actualiza el campo area_responsable de dw.dim_proyecto usando
#   los datos del consolidado_proyectos. Solo actualiza registros donde
#   el campo está vacío o NULL, preservando valores ya existentes.
#
#   Usa DISTINCT ON para tomar un único valor por proyecto, evitando
#   conflictos cuando hay múltiples filas por proyecto en staging.
#
# Dependencias:
#   - Requiere SP_CARGA_FACT_PAGO completado (o al menos dimensiones cargadas)
#   - Requiere stg.consolidado_proyectos poblada
# ==============================================================================
SQL_UPDATE_AREA_RESPONSABLE = """
UPDATE dw.dim_proyecto dp
SET area_responsable = sub.area_responsable_proyecto
FROM (
    SELECT DISTINCT ON (codigo_proyecto)
        codigo_proyecto,
        area_responsable_proyecto
    FROM stg.consolidado_proyectos
    WHERE area_responsable_proyecto IS NOT NULL
      AND area_responsable_proyecto != ''
    ORDER BY codigo_proyecto
) sub
WHERE dp.codigo_proyecto = sub.codigo_proyecto
  AND (dp.area_responsable IS NULL OR dp.area_responsable = '')
"""

@medir_tiempo("UPDATE_AREA_RESPONSABLE")
def update_area_responsable() -> int:
    """Actualiza area_responsable en dim_proyecto desde consolidado (v2)."""
    return execute_sql(CONN_DWH_LOCAL, SQL_UPDATE_AREA_RESPONSABLE, "UPDATE_AREA_RESPONSABLE")


# ==============================================================================
# PASO 15: Bridge Proyecto-Geografía (v2)
# ==============================================================================
# Equivalente Pentaho: SP Bridge Proyecto-Geografia (entrada tipo SQL)
# Stored Procedure: dw.sp_carga_proyecto_geografia()
#
# Descripción:
#   Puebla la bridge table dw.fact_proyecto_geografia que resuelve la
#   relación muchos-a-muchos entre proyectos y ubicaciones geográficas.
#
#   Un proyecto puede tener múltiples ubicaciones (provincia/cantón/parroquia)
#   y esta tabla las vincula con sus claves surrogadas. Además, marca
#   la ubicación principal (es_principal = true) basándose en la tarea
#   más reciente del proyecto.
#
# Dependencias:
#   - Requiere dim_proyecto y dim_geografia pobladas
# ==============================================================================
@medir_tiempo("SP_BRIDGE_PROYECTO_GEO")
def sp_bridge_proyecto_geo():
    """Ejecuta dw.sp_carga_proyecto_geografia() — Bridge table proyecto-ubicación."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_carga_proyecto_geografia()", "SP_BRIDGE_PROYECTO_GEO")


# ==============================================================================
# PASO 17: Recálculo de Montos JBPM (v3)
# ==============================================================================
# Equivalente Pentaho: Recalculo Montos JBPM (entrada tipo SQL)
#
# Descripción:
#   Corrige el campo monto_transaccion en fact_pago para pagos JBPM
#   usando el historial de saldos de online_payments_historical.
#
#   ALGORITMO:
#   1. Filtra registros históricos con description = 'Uso de transacción'
#   2. Ordena por id_online_payment_historical (secuencia temporal)
#   3. Usa LAG() para obtener el saldo anterior (value_updated del registro previo)
#   4. Calcula el monto real como: saldo_anterior - saldo_actual
#   5. Actualiza fact_pago solo donde origen = 'JBPM'
#
#   NOTA: Para el primer registro de cada secuencia (sin registro previo),
#   el saldo anterior se calcula como: value_updated + retired_value
#   (reconstruyendo el saldo original antes del retiro).
#
# Dependencias:
#   - Requiere TRX_09 (online_payments_historical_bi) poblada
#   - Requiere SP_CARGA_FACT_PAGO completado
# ==============================================================================
SQL_RECALCULO_MONTOS = """
WITH desc_saldos AS (
    SELECT
        TRIM(oph.project_id) AS project_id,
        TRIM(oph.tramit_number) AS tramit_number,
        COALESCE(
            LAG(REPLACE(oph.value_updated, ',', '.')::numeric) OVER (
                PARTITION BY TRIM(oph.tramit_number)
                ORDER BY oph.id_online_payment_historical ASC
            ),
            (
                REPLACE(oph.value_updated, ',', '.')::numeric
                + REPLACE(COALESCE(oph.retired_value, '0'), ',', '.')::numeric
            )
        ) AS saldo_anterior,
        REPLACE(oph.value_updated, ',', '.')::numeric AS saldo_actual
    FROM stg.online_payments_historical_bi oph
    WHERE oph.description = 'Uso de transacción'
        AND TRIM(oph.project_id) IS NOT NULL
        AND TRIM(oph.project_id) != ''
),
calculado AS (
    SELECT
        project_id,
        tramit_number,
        (saldo_anterior - saldo_actual) AS valor_calculado
    FROM desc_saldos
)
UPDATE dw.fact_pago fp
SET monto_transaccion = c.valor_calculado,
    monto_pagado = c.valor_calculado
FROM calculado c
    INNER JOIN dw.dim_proyecto dp ON dp.codigo_proyecto = c.project_id
WHERE fp.sk_proyecto = dp.sk_proyecto
    AND fp.numero_tramite = c.tramit_number
    AND fp.origen = 'JBPM'
"""

@medir_tiempo("RECALCULO_MONTOS_JBPM")
def recalculo_montos_jbpm() -> int:
    """Recalcula monto_transaccion en fact_pago usando saldos históricos (v3)."""
    return execute_sql(CONN_DWH_LOCAL, SQL_RECALCULO_MONTOS, "RECALCULO_MONTOS_JBPM")


# ==============================================================================
# PASO 18: Calcular Secuencia de Pagos (v2/v3)
# ==============================================================================
# Equivalente Pentaho: SP Calcular Secuencia Pagos (entrada tipo SQL)
# Stored Procedure: dw.sp_calcular_secuencia_pagos()
#
# Descripción:
#   Calcula el número de secuencia, el indicador de depósito inicial
#   y el monto acumulado para cada pago agrupado por numero_tramite.
#
#   Campos actualizados en fact_pago:
#     - secuencia_pago:      ROW_NUMBER() dentro de cada tramit_number,
#                            ordenado por fecha de pago
#     - es_deposito_inicial: true si secuencia_pago = 1
#     - monto_acumulado:     SUM() acumulativa de monto_transaccion
#
#   Este paso se ejecuta al final del proceso para que considere todos
#   los pagos, incluyendo los montos recalculados por el paso anterior.
#
# Dependencias:
#   - Requiere RECALCULO_MONTOS_JBPM completado (o SP_CARGA_FACT_PAGO si no hay v3)
# ==============================================================================
@medir_tiempo("SP_SECUENCIA_PAGOS")
def sp_secuencia_pagos():
    """Ejecuta dw.sp_calcular_secuencia_pagos() — Secuencia y acumulado de pagos."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_calcular_secuencia_pagos()", "SP_SECUENCIA_PAGOS")

# ==============================================================================
# PASO 19: Cargar Dimensión de Área (v1.1)
# ==============================================================================
# Stored Procedure: dw.sp_carga_dim_area()
#
# Descripción:
#   Puebla dw.dim_area desde stg.suia_areas_bi.
#
# Dependencias:
#   - Requiere TRX_10_AREAS completado
# ==============================================================================
@medir_tiempo("SP_CARGA_DIM_AREA")
def sp_carga_dim_area():
    """Ejecuta dw.sp_carga_dim_area() — Puebla dim_area desde suia_enlisy."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_carga_dim_area()", "SP_CARGA_DIM_AREA")
# ==============================================================================
# PASO 11: Orquestar Extracción Remota (v1.4.1)
# ==============================================================================
# Stored Procedure: dw.sp_orquestar_extraccion_remota()
#
# Descripción:
#   Dispara las funciones suia_iii.sp_coa_bi_v1_4_1() y
#   coa_mae.sp_rcoa_bi_v1_4_1() en el servidor remoto 172.16.0.179.
#   Asegura que las tablas tmp estén pobladas con datos multicanal.
# ==============================================================================
@medir_tiempo("SP_ORQUESTAR_EXTRACCION")
def sp_orquestar_extraccion_remota():
    """Ejecuta dw.sp_orquestar_extraccion_remota() — Dispara SPs v1.4.1."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_orquestar_extraccion_remota()", "SP_ORQUESTAR_EXTRACCION")


# ==============================================================================
# PASO 12: Cargar Puente Ambiental (v1.4.1)
# ==============================================================================
# Stored Procedure: dw.sp_carga_puente_ambiental()
#
# Descripción:
#   Parsea la columna 'AREAS PROTEGIDAS' del consolidado y puebla la bridge table
#   dw.bridge_interseccion_ambiental, mapeando con dw.dim_capa_ambiental.
# ==============================================================================
@medir_tiempo("SP_CARGA_PUENTE_AMBIENTAL")
def sp_carga_puente_ambiental():
    """Ejecuta dw.sp_carga_puente_ambiental() — Puebla bridge table biodiversidad."""
    execute_sp(CONN_DWH_LOCAL, "SELECT dw.sp_carga_puente_ambiental()", "SP_CARGA_PUENTE_AMBIENTAL")

# ==============================================================================
# PASO 13: Cargar Desechos Peligrosos y Sustancias Químicas (v1.5)
# ==============================================================================
# Ejecuta los scripts SQL generados para transformar datos desde Staging hacia
# el DW local usando logic nativa MERGE/INSERT.
# ==============================================================================
@medir_tiempo("SP_CARGA_WASTE_CHEMICAL")
def sp_carga_waste_chemical():
    """Ejecuta los scripts DML (Data Manipulation) de desechos peligrosos."""
    from config import PROJECT_ROOT
    ruta_load = os.path.join(PROJECT_ROOT, "etl_waste_chemical_load.sql")
    with open(ruta_load, "r", encoding="utf-8") as f:
        sql_load = f.read()
    
    execute_sql(CONN_DWH_LOCAL, sql_load, "SP_CARGA_WASTE_CHEMICAL")


# ==============================================================================
# PASO 28: Cargar Dimensión de Intersección Ambiental (v1.9.1)
# ==============================================================================
# Script SQL: etl_intersection_load.sql
#
# Descripción:
#   Carga dw.dim_intersection desde stg.stg_intersection con lógica UPSERT.
#   Previamente la ingesta (ingesta_intersection.py) ha consolidado las capas
#   geográficas (SNAP, Bosques Protectores, Patrimonio Forestal, Zonas
#   Intangibles) y las variables BPM en un dictamen final HTML.
#
#   Pasos internos:
#     1. Marca registros obsoletos como is_current = FALSE
#     2. UPSERT (INSERT ON CONFLICT DO UPDATE) de certificados actuales
#     3. ANALYZE para actualizar estadísticas
#
# Dependencias:
#   - Requiere INGESTA_INTERSECTION completado (stg.stg_intersection poblada)
#   - Requiere RECOVER_MISSING_PROJECTS completado (dim_proyecto sin huecos)
# ==============================================================================
@medir_tiempo("SP_CARGA_DIM_INTERSECTION")
def sp_carga_dim_intersection():
    """Ejecuta etl_intersection_load.sql — UPSERT de certificados de intersección."""
    from config import PROJECT_ROOT
    ruta_load = os.path.join(PROJECT_ROOT, "etl_intersection_load.sql")
    with open(ruta_load, "r", encoding="utf-8") as f:
        sql_load = f.read()

    execute_sql(CONN_DWH_LOCAL, sql_load, "SP_CARGA_DIM_INTERSECTION")
