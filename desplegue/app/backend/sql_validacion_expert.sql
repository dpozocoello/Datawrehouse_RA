/*
 ================================================================================
 SCRIPT DE VALIDACIÓN TÉCNICA - DATA WAREHOUSE REGULARIZACIÓN AMBIENTAL (v1.3)
 Arquitecto de Datos: DWH Team
 Objetivo: Auditoría de integridad, calidad e integridad geográfica.
 ================================================================================
 */
-- -----------------------------------------------------------------------------
-- 1. CONTROL DE INGESTA (STAGING)
-- -----------------------------------------------------------------------------
-- 1.1 Conteo de registros Áreas (Fuente vs Staging)
SELECT 'STAGING - Áreas' as tabla,
    COUNT(*)
FROM stg.suia_areas_bi
UNION ALL
SELECT 'DWH FINAL - Áreas',
    COUNT(*)
FROM dw.dim_area
WHERE sk_area > 0;
-- 1.2 Validación de carga del Catálogo Geográfico Nacional
SELECT COUNT(*) as total_nodos_geograficos,
    MIN(fecha_carga) as ultima_actualizacion
FROM stg.geographical_locations_bi;
-- 1.3 Detección de truncamientos en campos SNAP (Deberían ser TEXT)
SELECT sk_proyecto,
    length(interseccion_snap) as longitud_html
FROM dw.fact_regularizacion
WHERE length(interseccion_snap) > 1000
LIMIT 5;
-- -----------------------------------------------------------------------------
-- 2. INTEGRIDAD GEOGRÁFICA (V1.3 EXPERT)
-- -----------------------------------------------------------------------------
-- 2.1 Validación del Catálogo Maestro INEC (ref)
SELECT *
FROM ref.inec_dpa_2024
ORDER BY codigo_provincia;
-- 2.2 Auditoría de Provincias Resolvidas (Must be in ref catalog)
-- Este query identifica si alguna oficina técnica tiene una provincia que no está en el catálogo oficial.
SELECT nombre_area,
    provincia,
    canton
FROM dw.dim_area
WHERE sk_area > 0
    AND provincia NOT IN (
        SELECT nombre_provincia
        FROM ref.inec_dpa_2024
    );
-- 2.3 Verificación específica de Corrección Experta (Caso SALITRE)
-- El resultado esperado para Provincia es 'GUAYAS'.
SELECT id_area,
    nombre_area,
    provincia,
    canton
FROM dw.dim_area
WHERE nombre_area ILIKE '%SALITRE%';
-- 2.4 Áreas con geografía 'N/A' (Excluyendo el SK=0)
SELECT COUNT(*) as areas_sin_geografia
FROM dw.dim_area
WHERE sk_area > 0
    AND (
        provincia = 'N/A'
        OR provincia IS NULL
    );
-- -----------------------------------------------------------------------------
-- 3. INTEGRIDAD DEL MODELO ESTRELLA (FACTS & DIMS)
-- -----------------------------------------------------------------------------
-- 3.1 Registros huérfanos en Fact Table (Sin dimensión de área válida)
-- Si sk_area = 0, el proyecto no tiene oficina técnica vinculada en origen.
SELECT da.nombre_area,
    COUNT(f.*) as total_proyectos
FROM dw.fact_regularizacion f
    JOIN dw.dim_area da ON f.sk_area = da.sk_area
GROUP BY da.nombre_area
ORDER BY 2 DESC;
-- 3.2 Validación de la Categoría N/A (Standard SK=0)
SELECT *
FROM dw.dim_area
WHERE sk_area = 0;
SELECT *
FROM dw.dim_proyecto
WHERE sk_proyecto = 0;
-- 3.3 Verificación de duplicados en Dimensiones (Criterio de Unicidad)
SELECT id_area,
    COUNT(*)
FROM dw.dim_area
GROUP BY id_area
HAVING COUNT(*) > 1;
-- -----------------------------------------------------------------------------
-- 4. INTELIGENCIA DE PAGOS
-- -----------------------------------------------------------------------------
-- 4.1 Consistencia de totales por Proponente (Audit Nivel B)
-- Detectar si hay pagos inflados por error en la lógica indirecta.
SELECT sk_proponente,
    sum(monto_pagado) as total_recaudado
FROM dw.fact_pago
GROUP BY sk_proponente
ORDER BY 2 DESC
LIMIT 10;
-- 4.2 Origen de la Información de Pagos
SELECT origen,
    COUNT(*)
FROM dw.fact_pago
GROUP BY origen;
-- -----------------------------------------------------------------------------
-- 5. PERFORMANCE INDICATORS
-- -----------------------------------------------------------------------------
-- 5.1 Verificar existencia de índices críticos
SELECT tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname IN ('dw')
    AND tablename IN ('fact_regularizacion', 'fact_pago', 'dim_area');