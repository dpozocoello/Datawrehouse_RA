-- ==============================================================================
-- Consulta de verificación v2 — Pagos DWH con campos nuevos
-- Usa la bridge table para geografía principal y secuencia de pagos
-- ==============================================================================
SELECT dp.codigo_proyecto AS "CÓDIGO PROYECTO",
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
    -- Geografía desde bridge table (ubicación principal)
    dg.provincia AS "PROVINCIA",
    dg.canton AS "CANTON",
    dg.parroquia AS "PARROQUIA",
    -- Área responsable (campo nuevo v2)
    dp.area_responsable AS "ÁREA RESPONSABLE PROYECTO",
    f.proceso AS "PROCESO",
    de.estado_proceso AS "ESTADO PROCESO",
    f.fecha_inicio_proceso AS "FECHA INICIO PROCESO",
    f.fecha_fin_proceso AS "FECHA FIN PROCESO",
    f.tarea AS "TAREA",
    COALESCE(de.estado_tramite, de.estado_proyecto, 'N/A') AS "ESTADO TAREA",
    f.fecha_inicio_tarea AS "FECHA INICIO TAREA",
    f.fecha_fin_tarea AS "FECHA FIN TAREA",
    du.usuario_tarea AS "USUARIO TAREA",
    de.estado_proyecto AS "ESTADO PROYECTO",
    dp.sistema AS "SISTEMA",
    -- Datos de pago
    dpago.tipo_pago AS "TIPO PAGO",
    dpago.bank_code AS "CODIGO BANCO",
    fp.numero_tramite AS "TRAMITE PAGO",
    fp.monto_transaccion AS "VALOR TRANSACCION",
    fp.monto_pagado AS "VALOR PAGADO",
    dtp.fecha AS "FECHA TRANSACCION PAGO",
    dpago.transaction_type AS "TIPO TRANSACCION",
    fp.tarea_bpm AS "TAREA BPM",
    fp.proceso_bpm AS "PROCESO BPM",
    fp.origen AS "SISTEMA ORIGEN PAGO",
    -- Campos nuevos v2: secuencia de pagos
    fp.secuencia_pago AS "SECUENCIA PAGO",
    fp.es_deposito_inicial AS "ES DEPOSITO INICIAL",
    fp.monto_acumulado AS "MONTO ACUMULADO"
FROM (
        -- Subquery para obtener la fila principal por proyecto
        SELECT DISTINCT ON (fr.sk_proyecto) fr.*
        FROM dw.fact_regularizacion fr
            INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = fr.sk_proyecto
            INNER JOIN dw.dim_proponente dpp ON dpp.sk_proponente = fr.sk_proponente
            INNER JOIN dw.dim_estado de ON de.sk_estado = fr.sk_estado
        WHERE dp.tipo_permiso_ambiental = 'Registro Ambiental'
            AND de.estado_proyecto = 'Completado'
        ORDER BY fr.sk_proyecto,
            fr.fecha_fin_tarea DESC NULLS LAST
    ) f
    INNER JOIN dw.dim_proyecto dp ON dp.sk_proyecto = f.sk_proyecto
    INNER JOIN dw.dim_proponente dpp ON dpp.sk_proponente = f.sk_proponente
    INNER JOIN dw.dim_actividad da ON da.sk_actividad = f.sk_actividad
    INNER JOIN dw.dim_usuario du ON du.sk_usuario = f.sk_usuario
    INNER JOIN dw.dim_estado de ON de.sk_estado = f.sk_estado
    INNER JOIN dw.dim_tiempo dt ON dt.sk_tiempo = f.sk_fecha_registro -- Geografía: Usar bridge table para ubicación principal
    LEFT JOIN dw.fact_proyecto_geografia fpg ON fpg.sk_proyecto = f.sk_proyecto
    AND fpg.es_principal = true
    LEFT JOIN dw.dim_geografia dg ON dg.sk_geografia = fpg.sk_geografia -- Pagos
    LEFT JOIN dw.fact_pago fp ON fp.sk_proyecto = f.sk_proyecto
    LEFT JOIN dw.dim_pago dpago ON dpago.sk_pago = fp.sk_pago
    LEFT JOIN dw.dim_tiempo dtp ON dtp.sk_tiempo = fp.sk_fecha_pago
ORDER BY dp.codigo_proyecto;