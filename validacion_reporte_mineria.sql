-- ==============================================================================
-- VALIDACIÓN DE DISPONIBILIDAD DE DATOS PARA REPORTE DE MINERÍA
-- Base: dw_reg_v1 | Fecha: 2026-05-13
-- ==============================================================================
-- Objetivo: Verificar que cada uno de los 10 campos requeridos existe
-- en el DWH y cuantificar su cobertura (% de registros con dato vs NULL).
-- ==============================================================================

-- ==============================================================================
-- PASO 1: VERIFICAR EXISTENCIA DE COLUMNAS EN LAS DIMENSIONES
-- ==============================================================================
SELECT '--- COLUMNAS EN dim_proyecto ---' AS seccion;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_proyecto'
  AND column_name IN (
    'nombre_proyecto', 'codigo_proyecto', 'coordenada_x', 'coordenada_y',
    'sistema', 'tipo_sector', 'tipo_permiso_ambiental'
  )
ORDER BY ordinal_position;

SELECT '--- COLUMNAS EN dim_proponente ---' AS seccion;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_proponente'
  AND column_name IN (
    'nombre_proponente', 'ced_ruc_proponente',
    'correo_electronico', 'telefono'
  )
ORDER BY ordinal_position;

SELECT '--- COLUMNAS EN dim_actividad ---' AS seccion;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_actividad'
  AND column_name IN ('codigo_actividad', 'actividad_economica')
ORDER BY ordinal_position;

SELECT '--- COLUMNAS EN dim_geografia ---' AS seccion;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_geografia'
  AND column_name IN ('provincia', 'canton', 'parroquia')
ORDER BY ordinal_position;

SELECT '--- COLUMNAS EN dim_estado ---' AS seccion;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'dw' AND table_name = 'dim_estado'
  AND column_name IN ('estado_proyecto', 'estado_tramite', 'estado_proceso')
ORDER BY ordinal_position;

-- ==============================================================================
-- PASO 2: CONTEO GENERAL DE REGISTROS EN fact_regularizacion
-- ==============================================================================
SELECT '--- UNIVERSO DE DATOS ---' AS seccion;
SELECT
    COUNT(*)                                          AS total_registros,
    COUNT(DISTINCT fr.sk_proyecto)                    AS proyectos_unicos,
    COUNT(DISTINCT fr.sk_proponente)                  AS proponentes_unicos,
    COUNT(DISTINCT dg.provincia)                      AS provincias_distintas
FROM dw.fact_regularizacion fr
JOIN dw.dim_geografia dg ON dg.sk_geografia = fr.sk_geografia;

-- ==============================================================================
-- PASO 3: COBERTURA DE CADA CAMPO REQUERIDO (sobre el total de proyectos)
-- ==============================================================================
SELECT '--- COBERTURA DE CAMPOS (% con dato) ---' AS seccion;
SELECT
    COUNT(DISTINCT dp.codigo_proyecto) AS total_proyectos,

    -- 1. Nombre Proyecto
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dp.nombre_proyecto IS NOT NULL
                AND dp.nombre_proyecto != ''
                AND dp.nombre_proyecto != 'N/A')     AS con_nombre,

    -- 2. Código Proyecto (siempre presente por PK)
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dp.codigo_proyecto IS NOT NULL) AS con_codigo,

    -- 3. Representante Legal
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dpr.nombre_proponente IS NOT NULL
                AND dpr.nombre_proponente != '')      AS con_representante,

    -- 4. CIIU
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE da.codigo_actividad IS NOT NULL
                AND da.codigo_actividad != '')        AS con_ciiu,

    -- 5. Provincia
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dg.provincia IS NOT NULL
                AND dg.provincia != 'N/A')            AS con_provincia,

    -- 6. Cantón
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dg.canton IS NOT NULL
                AND dg.canton != 'N/A')               AS con_canton,

    -- 7. Coordenadas
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dp.coordenada_x IS NOT NULL)    AS con_coordenadas,

    -- 8. Estado
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE de.estado_proyecto IS NOT NULL
                AND de.estado_proyecto != 'N/A')      AS con_estado,

    -- 9. Correo
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dpr.correo_electronico IS NOT NULL
                AND dpr.correo_electronico != '')      AS con_correo,

    -- 10. Teléfono
    COUNT(DISTINCT dp.codigo_proyecto)
        FILTER (WHERE dpr.telefono IS NOT NULL
                AND dpr.telefono != '')                AS con_telefono

FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp    ON dp.sk_proyecto   = fr.sk_proyecto
JOIN dw.dim_proponente dpr ON dpr.sk_proponente = fr.sk_proponente
LEFT JOIN dw.dim_actividad da ON da.sk_actividad = fr.sk_actividad
JOIN dw.dim_geografia dg   ON dg.sk_geografia  = fr.sk_geografia
LEFT JOIN dw.dim_estado de ON de.sk_estado     = fr.sk_estado;

-- ==============================================================================
-- PASO 4: VALORES DISPONIBLES PARA LOS FILTROS DINÁMICOS
-- ==============================================================================

-- 4.1 Provincias disponibles (para filtro seleccionable)
SELECT '--- PROVINCIAS DISPONIBLES ---' AS seccion;
SELECT DISTINCT UPPER(TRIM(dg.provincia)) AS provincia,
    COUNT(DISTINCT dp.codigo_proyecto) AS num_proyectos
FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp   ON dp.sk_proyecto  = fr.sk_proyecto
JOIN dw.dim_geografia dg  ON dg.sk_geografia = fr.sk_geografia
WHERE dg.provincia IS NOT NULL AND dg.provincia != 'N/A'
GROUP BY UPPER(TRIM(dg.provincia))
ORDER BY num_proyectos DESC;

-- 4.2 Versiones del SUIA / Origen (para filtro seleccionable)
SELECT '--- VERSIONES SUIA / ORIGEN ---' AS seccion;
SELECT DISTINCT dp.sistema AS version_suia,
    COUNT(DISTINCT dp.codigo_proyecto) AS num_proyectos
FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp ON dp.sk_proyecto = fr.sk_proyecto
WHERE dp.sistema IS NOT NULL
GROUP BY dp.sistema
ORDER BY num_proyectos DESC;

-- 4.3 Sectores / Rubros de negocio (para filtro de Minería, Turístico, etc.)
SELECT '--- SECTORES / RUBROS (tipo_sector) ---' AS seccion;
SELECT DISTINCT dp.tipo_sector,
    COUNT(DISTINCT dp.codigo_proyecto) AS num_proyectos
FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp ON dp.sk_proyecto = fr.sk_proyecto
WHERE dp.tipo_sector IS NOT NULL AND dp.tipo_sector != ''
GROUP BY dp.tipo_sector
ORDER BY num_proyectos DESC;

-- 4.4 Tipos de permiso ambiental (complemento al filtro de sector)
SELECT '--- TIPOS DE PERMISO AMBIENTAL ---' AS seccion;
SELECT DISTINCT dp.tipo_permiso_ambiental,
    COUNT(DISTINCT dp.codigo_proyecto) AS num_proyectos
FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp ON dp.sk_proyecto = fr.sk_proyecto
WHERE dp.tipo_permiso_ambiental IS NOT NULL AND dp.tipo_permiso_ambiental != ''
GROUP BY dp.tipo_permiso_ambiental
ORDER BY num_proyectos DESC;

-- ==============================================================================
-- PASO 5: PRUEBA DE REPORTE FINAL (Muestra de 20 registros)
-- Con todas las provincias solicitadas y filtros aplicables
-- ==============================================================================
SELECT '--- MUESTRA DEL REPORTE (20 registros) ---' AS seccion;
SELECT DISTINCT
    dp.nombre_proyecto                              AS "Nombre del Proyecto",
    dp.codigo_proyecto                              AS "Código de Proyecto",
    dpr.nombre_proponente                           AS "Representante Legal",
    COALESCE(da.codigo_actividad || ' - ' || da.actividad_economica, 'N/A') AS "CIIU",
    dg.provincia                                    AS "Provincia",
    dg.canton                                       AS "Cantón",
    dp.coordenada_x                                 AS "Coordenada X",
    dp.coordenada_y                                 AS "Coordenada Y",
    COALESCE(de.estado_proyecto, de.estado_tramite) AS "Estado",
    dpr.correo_electronico                          AS "Correo Electrónico",
    dpr.telefono                                    AS "Teléfono",
    -- Campos para filtros dinámicos:
    dp.sistema                                      AS "Versión SUIA",
    dp.tipo_sector                                  AS "Sector (Rubro)",
    dp.tipo_permiso_ambiental                       AS "Tipo Permiso"
FROM dw.fact_regularizacion fr
    JOIN dw.dim_proyecto dp    ON dp.sk_proyecto   = fr.sk_proyecto
    JOIN dw.dim_proponente dpr ON dpr.sk_proponente = fr.sk_proponente
    LEFT JOIN dw.dim_actividad da ON da.sk_actividad = fr.sk_actividad
    JOIN dw.dim_geografia dg   ON dg.sk_geografia  = fr.sk_geografia
    LEFT JOIN dw.dim_estado de ON de.sk_estado     = fr.sk_estado
WHERE
    UPPER(TRIM(dg.provincia)) IN (
        'COTOPAXI', 'AZUAY', 'IMBABURA', 'MORONA SANTIAGO',
        'EL ORO', 'ZAMORA CHINCHIPE', 'NAPO', 'SUCUMBÍOS', 'SUCUMBIOS', 'LOJA'
    )
ORDER BY dg.provincia, dp.codigo_proyecto
LIMIT 20;

-- ==============================================================================
-- FIN DE LA VALIDACIÓN
-- ==============================================================================
