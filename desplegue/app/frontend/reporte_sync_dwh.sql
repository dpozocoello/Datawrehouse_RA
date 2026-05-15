-- ============================================================
--  REPORTE DE SINCRONIZACIÓN DWH — ECO-SIEAA
--  Base de datos: dw_reg_v1   Esquema: dw
--  Ejecutar en DBeaver conectado a: localhost:5432
--  Fecha de consulta: 04/05/2026
-- ============================================================
-- INSTRUCCIÓN: Ejecute cada bloque de forma independiente (F5 o Ctrl+Enter)
--              seleccionando solo el bloque deseado, o ejecute todo junto.
-- ============================================================


-- ===========================================================
-- BLOQUE 1: RESUMEN GENERAL DE SINCRONIZACIÓN POR ORIGEN ETL
-- Confirma la fecha más reciente de datos por fuente
-- Equivale al panel "DETALLE POR ORIGEN ETL" del Dashboard
-- ===========================================================
SELECT
    f.origen                                        AS "Origen ETL",
    COUNT(*)                                        AS "Total Registros DW",
    TO_CHAR(MIN(f.fecha_carga), 'DD/MM/YYYY HH24:MI')  AS "Primera Carga DW",
    TO_CHAR(MAX(f.fecha_carga), 'DD/MM/YYYY HH24:MI')  AS "Última Carga DW",
    TO_CHAR(MIN(f.fecha_inicio_proceso), 'DD/MM/YYYY')  AS "Dato Más Antiguo (Origen)",
    TO_CHAR(MAX(f.fecha_inicio_proceso), 'DD/MM/YYYY')  AS "Dato Más Reciente (Origen)"
FROM dw.fact_regularizacion f
GROUP BY f.origen
ORDER BY
    CASE f.origen
        WHEN 'JBPM_HIDRO'   THEN 1
        WHEN 'JBPM_SECTOR'  THEN 2
        WHEN 'JBPM_4CAT'    THEN 3
        WHEN 'COA'          THEN 4
        WHEN 'RCOA'         THEN 5
        ELSE 6
    END;


-- ===========================================================
-- BLOQUE 2: RESUMEN GLOBAL DEL DWH
-- Valida los datos que muestra el widget principal del sidebar
-- ("1,227,102 registros · datos hasta 29/04/2026")
-- ===========================================================
SELECT
    COUNT(*)                                            AS "Total Registros DWH",
    TO_CHAR(MAX(f.fecha_carga),        'DD/MM/YYYY HH24:MI') AS "Última Carga ETL",
    TO_CHAR(MAX(f.fecha_inicio_proceso),'DD/MM/YYYY')         AS "Fecha Dato Más Reciente",
    COUNT(DISTINCT p.codigo_proyecto)                   AS "Proyectos Únicos",
    COUNT(DISTINCT f.origen)                            AS "Orígenes ETL Activos"
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
  AND p.codigo_proyecto  != 'N/A'
  AND p.nombre_proyecto  != 'N/A';


-- ===========================================================
-- BLOQUE 3: DETALLE EXACTO POR ORIGEN (vista v_integridad_dashboard)
-- Replica la consulta que usa el dashboard directamente
-- ===========================================================
SELECT *
FROM dw.v_integridad_dashboard
ORDER BY
    CASE origen
        WHEN 'JBPM_HIDRO'   THEN 1
        WHEN 'JBPM_SECTOR'  THEN 2
        WHEN 'JBPM_4CAT'    THEN 3
        WHEN 'COA'          THEN 4
        WHEN 'RCOA'         THEN 5
        ELSE 6
    END ASC;


-- ===========================================================
-- BLOQUE 4: VALIDACIÓN DE BRECHA DE SINCRONIZACIÓN
-- Calcula cuántos días han pasado desde el último dato
-- por cada origen ETL (brecha entre dato más reciente y HOY)
-- ===========================================================
SELECT
    f.origen                                                 AS "Origen ETL",
    MAX(f.fecha_inicio_proceso)::DATE                        AS "Último Dato en Producción",
    CURRENT_DATE                                             AS "Fecha Consulta",
    (CURRENT_DATE - MAX(f.fecha_inicio_proceso)::DATE)       AS "Días Sin Nuevos Datos",
    CASE
        WHEN (CURRENT_DATE - MAX(f.fecha_inicio_proceso)::DATE) <= 1  THEN '🟢 AL DÍA'
        WHEN (CURRENT_DATE - MAX(f.fecha_inicio_proceso)::DATE) <= 7  THEN '🟡 RECIENTE (< 7 días)'
        WHEN (CURRENT_DATE - MAX(f.fecha_inicio_proceso)::DATE) <= 30 THEN '🟠 DESFASE MODERADO'
        ELSE                                                             '🔴 DESFASE CRÍTICO'
    END                                                      AS "Estado Sincronización",
    MAX(f.fecha_carga)                                       AS "Última Ejecución ETL"
FROM dw.fact_regularizacion f
GROUP BY f.origen
ORDER BY (CURRENT_DATE - MAX(f.fecha_inicio_proceso)::DATE) DESC;


-- ===========================================================
-- BLOQUE 5: VERIFICACIÓN DE INTEGRIDAD DE DIMENSIONES
-- Cuenta registros en cada tabla del DWH
-- ===========================================================
SELECT 'fact_regularizacion'   AS "Tabla",  COUNT(*) AS "Registros" FROM dw.fact_regularizacion
UNION ALL
SELECT 'fact_pago',                          COUNT(*) FROM dw.fact_pago
UNION ALL
SELECT 'dim_proyecto',                       COUNT(*) FROM dw.dim_proyecto
UNION ALL
SELECT 'dim_estado',                         COUNT(*) FROM dw.dim_estado
UNION ALL
SELECT 'dim_usuario',                        COUNT(*) FROM dw.dim_usuario
UNION ALL
SELECT 'dim_area',                           COUNT(*) FROM dw.dim_area
UNION ALL
SELECT 'dim_geografia',                      COUNT(*) FROM dw.dim_geografia
UNION ALL
SELECT 'dim_proponente',                     COUNT(*) FROM dw.dim_proponente
UNION ALL
SELECT 'dim_pago',                           COUNT(*) FROM dw.dim_pago
UNION ALL
SELECT 'dim_tiempo',                         COUNT(*) FROM dw.dim_tiempo
ORDER BY "Registros" DESC;


-- ===========================================================
-- BLOQUE 6: REPORTE COMPARATIVO vs. DASHBOARD
-- Compara lo que muestra el dashboard con lo que hay en BD
-- (basado en la imagen: COA 415,606 | RCOA 512,933 |
--  JBPM_4CAT 212,384 | JBPM_SECTOR 79,302 | JBPM_HIDRO 6,787)
-- ===========================================================
WITH dashboard_referencia AS (
    SELECT 'COA'         AS origen, 415606 AS regs_dashboard, DATE '2026-04-29' AS fecha_dashboard
    UNION ALL
    SELECT 'RCOA',        512933,  DATE '2026-04-29'
    UNION ALL
    SELECT 'JBPM_4CAT',  212384,  DATE '2025-10-13'
    UNION ALL
    SELECT 'JBPM_SECTOR', 79302,  DATE '2025-07-01'
    UNION ALL
    SELECT 'JBPM_HIDRO',   6787,  DATE '2025-06-26'
),
bd_actual AS (
    SELECT
        f.origen,
        COUNT(*)                              AS regs_bd,
        MAX(f.fecha_inicio_proceso)::DATE     AS fecha_bd
    FROM dw.fact_regularizacion f
    GROUP BY f.origen
)
SELECT
    COALESCE(d.origen, b.origen)             AS "Origen ETL",
    d.regs_dashboard                         AS "Regs Dashboard (imagen)",
    b.regs_bd                                AS "Regs BD Actual",
    (b.regs_bd - COALESCE(d.regs_dashboard,0)) AS "Diferencia (+nuevo/-perdido)",
    TO_CHAR(d.fecha_dashboard, 'DD/MM/YYYY') AS "Fecha Dashboard",
    TO_CHAR(b.fecha_bd, 'DD/MM/YYYY')        AS "Fecha BD Actual",
    CASE
        WHEN b.regs_bd = d.regs_dashboard    THEN '✅ IGUAL'
        WHEN b.regs_bd > d.regs_dashboard    THEN '📈 BD tiene más registros'
        WHEN b.regs_bd < d.regs_dashboard    THEN '📉 BD tiene menos (posible filtro)'
        ELSE '⚠️ No comparado'
    END                                      AS "Estado Comparativo"
FROM dashboard_referencia d
FULL OUTER JOIN bd_actual b ON d.origen = b.origen
ORDER BY
    CASE COALESCE(d.origen, b.origen)
        WHEN 'COA'          THEN 1
        WHEN 'RCOA'         THEN 2
        WHEN 'JBPM_4CAT'   THEN 3
        WHEN 'JBPM_SECTOR' THEN 4
        WHEN 'JBPM_HIDRO'  THEN 5
        ELSE 6
    END;


-- ===========================================================
-- BLOQUE 7: REGISTRO DE ACTIVIDAD RECIENTE (últimos 7 días)
-- Valida qué datos llegaron en la última ejecución ETL
-- ===========================================================
SELECT
    f.origen                                        AS "Origen ETL",
    f.fecha_carga::DATE                             AS "Fecha Carga ETL",
    COUNT(*)                                        AS "Registros Cargados",
    MIN(f.fecha_inicio_proceso)::DATE               AS "Dato Más Antiguo Lote",
    MAX(f.fecha_inicio_proceso)::DATE               AS "Dato Más Reciente Lote"
FROM dw.fact_regularizacion f
WHERE f.fecha_carga >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY f.origen, f.fecha_carga::DATE
ORDER BY f.fecha_carga::DATE DESC, f.origen;


-- ===========================================================
-- BLOQUE 8: CONTROL ETL (si existe tabla de control)
-- Verifica si hay tabla de control de ejecuciones ETL
-- ===========================================================
SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'dw'
  AND table_name IN ('etl_control', 'etl_log', 'etl_control_carga', 'carga_log',
                     'control_etl', 'log_carga', 'sync_log', 'etl_audit')
ORDER BY table_name;

-- *** Si la consulta anterior devuelve una tabla, use el nombre aquí:
-- SELECT * FROM dw.<nombre_tabla_control> ORDER BY fecha_fin DESC LIMIT 20;


-- ===========================================================
-- BLOQUE 9: RESUMEN EJECUTIVO FINAL (Una sola vista)
-- Consolida todo en un único resultado para el reporte
-- ===========================================================
SELECT
    '🗓️  CONSULTA REALIZADA'     AS "Métrica",
    TO_CHAR(NOW(), 'DD/MM/YYYY HH24:MI:SS') AS "Valor"
UNION ALL
SELECT
    '📦 TOTAL REGISTROS DWH',
    TO_CHAR(COUNT(*), 'FM9,999,999')
FROM dw.fact_regularizacion
UNION ALL
SELECT
    '📅 DATO MÁS RECIENTE EN PRODUCCIÓN',
    TO_CHAR(MAX(fecha_inicio_proceso)::DATE, 'DD/MM/YYYY')
FROM dw.fact_regularizacion
UNION ALL
SELECT
    '⏱️  ÚLTIMA EJECUCIÓN ETL',
    TO_CHAR(MAX(fecha_carga), 'DD/MM/YYYY HH24:MI')
FROM dw.fact_regularizacion
UNION ALL
SELECT
    '📊 DÍAS DESDE ÚLTIMA SINCRONIZACIÓN',
    (CURRENT_DATE - MAX(fecha_inicio_proceso)::DATE)::TEXT || ' días'
FROM dw.fact_regularizacion
UNION ALL
SELECT
    '🔄 ORÍGENES ETL ACTIVOS',
    COUNT(DISTINCT origen)::TEXT
FROM dw.fact_regularizacion
UNION ALL
SELECT
    '🏗️  PROYECTOS ÚNICOS',
    TO_CHAR(COUNT(DISTINCT p.codigo_proyecto), 'FM9,999,999')
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
WHERE p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
  AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)';

-- ============================================================
-- FIN DEL REPORTE
-- Archivo: reporte_sync_dwh.sql
-- Base datos: dw_reg_v1 | Esquema: dw | Host: localhost:5432
-- ============================================================
