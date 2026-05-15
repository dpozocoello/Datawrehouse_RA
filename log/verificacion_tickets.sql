-- ==============================================================================
-- SCRIPT DE VERIFICACIÓN - Consultas Adaptadas al DW
-- Ejecutar contra dw_reg_v1 (localhost:5432)
-- ==============================================================================
-- ============ TICKET #10535091 - Proyectos DRA ============
-- Conteo de proyectos con código -RA-, no completados, desde 2020
SELECT 'TICKET_10535091_DRA' AS ticket,
    COUNT(DISTINCT dp.codigo_proyecto) AS proyectos_unicos,
    COUNT(*) AS filas_totales
FROM dw.fact_regularizacion f
    INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = f.sk_proyecto
    INNER JOIN dw.dim_estado de ON de.sk_estado = f.sk_estado
WHERE de.estado_proyecto NOT IN (
        'Completado',
        'Completado Digitalizado',
        'Completado No Favorable'
    )
    AND dp.codigo_proyecto ILIKE '%-RA-%'
    AND f.fecha_inicio_proceso >= '2020-01-01 00:00:00';
-- ============ TICKET #10535560 - Matriz Regularización (2 años) ============
SELECT 'TICKET_10535560_MATRIZ_2A' AS ticket,
    COUNT(DISTINCT dp.codigo_proyecto) AS proyectos_unicos,
    COUNT(*) AS filas_totales,
    SUM(
        CASE
            WHEN f.interseccion_snap = 'SI' THEN 1
            ELSE 0
        END
    ) AS con_snap,
    SUM(
        CASE
            WHEN f.interseccion_snap = 'NO' THEN 1
            ELSE 0
        END
    ) AS sin_snap
FROM dw.fact_regularizacion f
    INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = f.sk_proyecto
    INNER JOIN dw.dim_estado de ON de.sk_estado = f.sk_estado
    INNER JOIN dw.dim_tiempo dt ON dt.sk_tiempo = f.sk_fecha_registro
WHERE dt.fecha >= CURRENT_DATE - INTERVAL '2 years'
    AND de.estado_proceso = 'Completado';
-- ============ TICKET #10535560 - Matriz Regularización (10 años) ============
SELECT 'TICKET_10535560_MATRIZ_10A' AS ticket,
    COUNT(DISTINCT dp.codigo_proyecto) AS proyectos_unicos,
    COUNT(*) AS filas_totales,
    SUM(
        CASE
            WHEN f.interseccion_snap = 'SI' THEN 1
            ELSE 0
        END
    ) AS con_snap
FROM dw.fact_regularizacion f
    INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = f.sk_proyecto
    INNER JOIN dw.dim_estado de ON de.sk_estado = f.sk_estado
    INNER JOIN dw.dim_tiempo dt ON dt.sk_tiempo = f.sk_fecha_registro
WHERE dt.fecha >= CURRENT_DATE - INTERVAL '10 years'
    AND de.estado_proceso = 'Completado';
-- ============ TICKET #10536002 - Validación Pago ============
SELECT 'TICKET_10536002_PAGOS' AS ticket,
    COUNT(*) AS total_staging_jbpm,
    (
        SELECT COUNT(*)
        FROM stg.financial_transaction_bi
    ) AS total_staging_suia,
    (
        SELECT COUNT(*)
        FROM dw.fact_pago
    ) AS total_fact_pago,
    (
        SELECT COUNT(*)
        FROM dw.fact_pago
        WHERE origen = 'JBPM'
    ) AS pagos_jbpm,
    (
        SELECT COUNT(*)
        FROM dw.fact_pago
        WHERE origen = 'SUIA_RCOA'
    ) AS pagos_suia
FROM stg.online_payments_bi;
-- Ejemplo con tramit_number real del ticket original
SELECT 'EJEMPLO_PAGO_TRAMITE' AS test,
    COUNT(*) AS resultados_encontrados
FROM stg.online_payments_bi op
WHERE op.tramit_number ILIKE '%1835574341%';
-- ============ TICKET #10537181 - Reporte Operadores ============
SELECT 'TICKET_10537181_OPERADORES' AS ticket,
    COUNT(*) AS filas_totales,
    COUNT(DISTINCT dp.codigo_proyecto) AS proyectos_unicos
FROM dw.fact_regularizacion f
    INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = f.sk_proyecto
    INNER JOIN dw.dim_usuario du ON du.sk_usuario = f.sk_usuario
    INNER JOIN dw.dim_estado de ON de.sk_estado = f.sk_estado
WHERE du.usuario_tarea IN ('1722267786')
    AND de.estado_tramite IN (
        'EN TRÁMITE',
        'PROCESO FISICO',
        'EN TRÁMITE HASTA LLEGAR A PROCESO FÍSICO',
        'FINALIZADO EXITO',
        'FINALIZADO NO FAVORABLE'
    );
-- ============ RESUMEN GENERAL DEL DW ============
SELECT 'RESUMEN_DW' AS info,
    (
        SELECT COUNT(*)
        FROM dw.fact_regularizacion
    ) AS fact_regularizacion,
    (
        SELECT COUNT(*)
        FROM dw.dim_proyecto
    ) AS dim_proyecto,
    (
        SELECT COUNT(*)
        FROM dw.dim_proponente
    ) AS dim_proponente,
    (
        SELECT COUNT(*)
        FROM dw.dim_actividad
    ) AS dim_actividad,
    (
        SELECT COUNT(*)
        FROM dw.dim_geografia
    ) AS dim_geografia,
    (
        SELECT COUNT(*)
        FROM dw.dim_usuario
    ) AS dim_usuario,
    (
        SELECT COUNT(*)
        FROM dw.dim_estado
    ) AS dim_estado,
    (
        SELECT COUNT(*)
        FROM dw.dim_tiempo
    ) AS dim_tiempo,
    (
        SELECT COUNT(*)
        FROM dw.dim_pago
    ) AS dim_pago,
    (
        SELECT COUNT(*)
        FROM dw.fact_pago
    ) AS fact_pago;