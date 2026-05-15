-- ==============================================================================
-- CONSULTA CORREGIDA - PAGOS DWH CON INTEGRIDAD PRODUCCIÓN
-- Ejecutar en: DWH local (dw_reg_v1)
-- Fecha: 2026-03-01
-- ==============================================================================
-- CAMBIOS vs versión anterior:
-- 1. ESTADO TAREA: Aplica CASE transform (Completado → FINALIZADO EXITO)
--    para coincidir con producción.
-- 2. PAGOS: Ahora usa la nueva fact_pago que incluye asociación por
--    tramit_number (múltiples proyectos por pago).
-- ==============================================================================
WITH local_projects AS (
    SELECT DISTINCT ON (dp.codigo_proyecto) dp.codigo_proyecto AS "CÓDIGO PROYECTO",
        dp.nombre_proyecto AS "NOMBRE PROYECTO",
        dt.fecha AS "FECHA REGISTRO",
        da.codigo_actividad AS "CÓDIGO ACTIVIDAD",
        da.actividad_economica AS "ACTIVIDAD ECONÓMICA",
        dpp.ced_ruc_proponente AS "CED/RUC PROPONENTE",
        dpp.nombre_proponente AS "NOMBRE PROPONENTE",
        f.nombre_zona AS "NOMBRE ZONA",
        dp.tipo_sector AS "TIPO SECTOR",
        dp.tipo_permiso_ambiental AS "TIPO PERMISO AMBIENTAL",
        dp.tipo_ente AS "TIPO ENTE",
        dg.provincia AS "PROVINCIA",
        dg.canton AS "CANTON",
        dg.parroquia AS "PARROQUIA",
        f.proceso AS "PROCESO",
        de.estado_proceso AS "ESTADO PROCESO",
        f.fecha_inicio_proceso AS "FECHA INICIO PROCESO",
        f.fecha_fin_proceso AS "FECHA FIN PROCESO",
        f.tarea AS "TAREA",
        -- ═══════════ ESTADO TAREA ═══════════
        -- Producción NO transforma este valor para Registro Ambiental.
        -- Se usa el valor raw de dim_estado para coincidir con producción.
        COALESCE(de.estado_tramite, de.estado_proyecto, 'N/A') AS "ESTADO TAREA",
        -- ═════════════════════════════════════════
        f.fecha_inicio_tarea AS "FECHA INICIO TAREA",
        f.fecha_fin_tarea AS "FECHA FIN TAREA",
        du.usuario_tarea AS "USUARIO TAREA",
        de.estado_proyecto AS "ESTADO PROYECTO",
        dp.sistema AS "SISTEMA"
    FROM dw.fact_regularizacion f
        INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = f.sk_proyecto
        INNER JOIN dw.dim_proponente dpp ON dpp.sk_proponente = f.sk_proponente
        INNER JOIN dw.dim_actividad da ON da.sk_actividad = f.sk_actividad
        INNER JOIN dw.dim_geografia dg ON dg.sk_geografia = f.sk_geografia
        INNER JOIN dw.dim_usuario du ON du.sk_usuario = f.sk_usuario
        INNER JOIN dw.dim_estado de ON de.sk_estado = f.sk_estado
        INNER JOIN dw.dim_tiempo dt ON dt.sk_tiempo = f.sk_fecha_registro
    WHERE dp.tipo_permiso_ambiental IN ('Registro Ambiental')
        AND de.estado_proyecto IN ('Completado')
        AND dpp.nombre_proponente ILIKE (
            'EMPRESA PUBLICA MUNICIPAL DE TELECOMUNICACIONES, AGUA POTABLE, ALCANTARILLADO Y SANEAMIENTO DE CUENCA%'
        )
        AND f.fecha_fin_proceso BETWEEN '2017-01-01 00:00:00' AND '2018-05-16 23:59:59'
    ORDER BY dp.codigo_proyecto,
        f.fecha_fin_tarea DESC
),
pagos_proyecto AS (
    -- Pagos locales desde dw.fact_pago (sin dblink)
    -- AHORA incluye pagos directos Y por tramit_number
    SELECT dp.codigo_proyecto AS project_id,
        dpago.tipo_pago AS "TIPO PAGO",
        dpago.bank_code AS bank_code,
        dpago.transaction_type AS transaction_type,
        fp.numero_tramite AS tramit_number,
        fp.monto_transaccion AS payment_value,
        fp.monto_pagado AS paid_value,
        fp.numero_transaccion AS convenience_number,
        dtp.fecha AS date_transaction,
        fp.tarea_bpm AS tarea_bpm,
        fp.proceso_bpm AS proceso_bpm,
        fp.origen AS sistema_pago
    FROM dw.fact_pago fp
        INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = fp.sk_proyecto
        INNER JOIN dw.dim_pago dpago ON dpago.sk_pago = fp.sk_pago
        LEFT JOIN dw.dim_tiempo dtp ON dtp.sk_tiempo = fp.sk_fecha_pago
)
SELECT lp.*,
    pp."TIPO PAGO" AS "TIPO PAGO",
    pp.bank_code AS "CODIGO BANCO",
    pp.tramit_number AS "TRAMITE PAGO",
    pp.payment_value AS "VALOR TRANSACCION",
    pp.paid_value AS "VALOR PAGADO",
    pp.date_transaction AS "FECHA TRANSACCION PAGO",
    pp.transaction_type AS "TIPO TRANSACCION",
    pp.tarea_bpm AS "TAREA BPM",
    pp.proceso_bpm AS "PROCESO BPM",
    pp.sistema_pago AS "SISTEMA ORIGEN PAGO"
FROM local_projects lp
    LEFT JOIN pagos_proyecto pp ON lp."CÓDIGO PROYECTO" = pp.project_id
ORDER BY lp."CÓDIGO PROYECTO";