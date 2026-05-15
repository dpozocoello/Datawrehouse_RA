-- ==============================================================================
-- REPORTE DE MINERÍA: PROYECTOS SUIA EMITIDOS Y EN TRÁMITE
-- Provincias: Cotopaxi, Azuay, Imbabura, Morona Santiago, El Oro,
--             Zamora Chinchipe, Napo, Sucumbíos, Loja
-- ==============================================================================
-- Base de datos: dw_reg_v1
-- Versión: v2.2 (con coordenadas, correo y teléfono)
-- ==============================================================================
-- EJECUCION:
--   psql -U postgres -d dw_reg_v1 -f reporte_mineria_proyectos.sql -o reporte_mineria.csv --csv
-- ==============================================================================

SELECT DISTINCT
    -- 1. Nombre del proyecto
    dp.nombre_proyecto                              AS "Nombre del Proyecto",
    -- 2. Código de proyecto
    dp.codigo_proyecto                              AS "Código de Proyecto",
    -- 3. Representante legal
    dpr.nombre_proponente                           AS "Representante Legal",
    -- 4. CIIU (Actividad Económica)
    da.codigo_actividad || ' - ' || da.actividad_economica AS "CIIU",
    -- 5. Provincia
    dg.provincia                                    AS "Provincia",
    -- 6. Cantón
    dg.canton                                       AS "Cantón",
    -- 7. Coordenadas (X, Y)
    dp.coordenada_x                                 AS "Coordenada X",
    dp.coordenada_y                                 AS "Coordenada Y",
    -- 8. Estado
    COALESCE(de.estado_proyecto, de.estado_tramite) AS "Estado",
    -- 9. Correo electrónico
    dpr.correo_electronico                          AS "Correo Electrónico",
    -- 10. Teléfono
    dpr.telefono                                    AS "Teléfono",
    -- Campos auxiliares para contexto
    dp.sistema                                      AS "Versión SUIA",
    dp.tipo_permiso_ambiental                       AS "Tipo Permiso Ambiental",
    dp.tipo_sector                                  AS "Sector",
    fr.origen                                       AS "Origen ETL"

FROM dw.fact_regularizacion fr
    INNER JOIN dw.dim_proyecto dp       ON dp.sk_proyecto = fr.sk_proyecto
    INNER JOIN dw.dim_proponente dpr    ON dpr.sk_proponente = fr.sk_proponente
    LEFT  JOIN dw.dim_actividad da      ON da.sk_actividad = fr.sk_actividad
    INNER JOIN dw.dim_geografia dg      ON dg.sk_geografia = fr.sk_geografia
    LEFT  JOIN dw.dim_estado de         ON de.sk_estado = fr.sk_estado

WHERE
    -- Filtro geográfico: las 9 provincias solicitadas
    UPPER(TRIM(dg.provincia)) IN (
        'COTOPAXI',
        'AZUAY',
        'IMBABURA',
        'MORONA SANTIAGO',
        'EL ORO',
        'ZAMORA CHINCHIPE',
        'NAPO',
        'SUCUMBÍOS',
        'SUCUMBIOS',
        'LOJA'
    )
    -- Filtro de estado: Emitidos y En Trámite
    AND (
        UPPER(COALESCE(de.estado_proyecto, '')) IN (
            'EMITIDO', 'EN TRÁMITE', 'EN TRAMITE',
            'ACTIVO', 'APROBADO', 'VIGENTE',
            'FINALIZADO', 'CERTIFICADO'
        )
        OR UPPER(COALESCE(de.estado_tramite, '')) IN (
            'EMITIDO', 'EN TRÁMITE', 'EN TRAMITE',
            'ACTIVO', 'APROBADO', 'VIGENTE',
            'FINALIZADO', 'CERTIFICADO'
        )
        -- Si no se filtrara por estado, descomente la siguiente línea:
        -- OR TRUE
    )

ORDER BY
    dg.provincia,
    dp.codigo_proyecto;

-- ==============================================================================
-- REPORTE ALTERNATIVO: SIN FILTRO DE ESTADO (TODOS los proyectos)
-- Descomentar si se requiere ver todos independientemente del estado
-- ==============================================================================
/*
SELECT DISTINCT
    dp.nombre_proyecto                              AS "Nombre del Proyecto",
    dp.codigo_proyecto                              AS "Código de Proyecto",
    dpr.nombre_proponente                           AS "Representante Legal",
    da.codigo_actividad || ' - ' || da.actividad_economica AS "CIIU",
    dg.provincia                                    AS "Provincia",
    dg.canton                                       AS "Cantón",
    dp.coordenada_x                                 AS "Coordenada X",
    dp.coordenada_y                                 AS "Coordenada Y",
    COALESCE(de.estado_proyecto, de.estado_tramite) AS "Estado",
    dpr.correo_electronico                          AS "Correo Electrónico",
    dpr.telefono                                    AS "Teléfono",
    dp.sistema                                      AS "Versión SUIA",
    fr.origen                                       AS "Origen ETL"
FROM dw.fact_regularizacion fr
    INNER JOIN dw.dim_proyecto dp       ON dp.sk_proyecto = fr.sk_proyecto
    INNER JOIN dw.dim_proponente dpr    ON dpr.sk_proponente = fr.sk_proponente
    LEFT  JOIN dw.dim_actividad da      ON da.sk_actividad = fr.sk_actividad
    INNER JOIN dw.dim_geografia dg      ON dg.sk_geografia = fr.sk_geografia
    LEFT  JOIN dw.dim_estado de         ON de.sk_estado = fr.sk_estado
WHERE
    UPPER(TRIM(dg.provincia)) IN (
        'COTOPAXI', 'AZUAY', 'IMBABURA', 'MORONA SANTIAGO',
        'EL ORO', 'ZAMORA CHINCHIPE', 'NAPO', 'SUCUMBÍOS', 'SUCUMBIOS', 'LOJA'
    )
ORDER BY dg.provincia, dp.codigo_proyecto;
*/

-- ==============================================================================
-- RESUMEN ESTADÍSTICO POR PROVINCIA
-- ==============================================================================
SELECT
    dg.provincia                                    AS "Provincia",
    COUNT(DISTINCT dp.codigo_proyecto)              AS "Total Proyectos",
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dp.coordenada_x IS NOT NULL)  AS "Con Coordenadas",
    COUNT(DISTINCT dpr.ced_ruc_proponente)
        FILTER (WHERE dpr.correo_electronico IS NOT NULL
                AND dpr.correo_electronico != '')    AS "Con Correo",
    COUNT(DISTINCT dpr.ced_ruc_proponente)
        FILTER (WHERE dpr.telefono IS NOT NULL
                AND dpr.telefono != '')              AS "Con Teléfono"
FROM dw.fact_regularizacion fr
    INNER JOIN dw.dim_proyecto dp       ON dp.sk_proyecto = fr.sk_proyecto
    INNER JOIN dw.dim_proponente dpr    ON dpr.sk_proponente = fr.sk_proponente
    INNER JOIN dw.dim_geografia dg      ON dg.sk_geografia = fr.sk_geografia
WHERE
    UPPER(TRIM(dg.provincia)) IN (
        'COTOPAXI', 'AZUAY', 'IMBABURA', 'MORONA SANTIAGO',
        'EL ORO', 'ZAMORA CHINCHIPE', 'NAPO', 'SUCUMBÍOS', 'SUCUMBIOS', 'LOJA'
    )
GROUP BY dg.provincia
ORDER BY "Total Proyectos" DESC;
