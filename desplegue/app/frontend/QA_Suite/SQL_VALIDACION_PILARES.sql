-- ==============================================================================
-- TOOLKIT DE VALIDACIÓN DE CALIDAD DE DATOS (5 PILARES)
-- PROYECTO: DASHBOARD RA V1.01
-- ROL: EXPERTO Q&A (20 AÑOS EXP.)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. EXACTITUD (ACCURACY)
-- Objetivo: El dato en el DW debe ser fiel al origen (Staging).
-- ------------------------------------------------------------------------------
-- 1.1 Comparación de totales Staging vs DW (Áreas)
SELECT 
    'STAGING (SUIA)' as origen, 
    COUNT(*) as total 
FROM stg.suia_areas_bi
UNION ALL
SELECT 
    'DW (DIM_AREA)', 
    COUNT(*) 
FROM dw.dim_area 
WHERE sk_area > 0;

-- 1.2 Verificación de exactitud por ID específico (Muestra)
-- Reemplazar ID según sea necesario para auditoría puntual.
SELECT 
    stg.id_area, 
    stg.provincia as fuente_prov, 
    dw.provincia as dw_prov
FROM stg.suia_areas_bi stg
JOIN dw.dim_area dw ON stg.id_area::text = dw.id_area::text
WHERE dw.sk_area > 0
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 2. COMPLETITUD (COMPLETENESS)
-- Objetivo: Ausencia de nulos en dimensiones y llaves mandatorias.
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) as registros_incompletos,
    'fact_regularizacion' as tabla
FROM dw.fact_regularizacion
WHERE sk_proyecto IS NULL 
   OR sk_geografia IS NULL 
   OR sk_area IS NULL;

-- ------------------------------------------------------------------------------
-- 3. CONSISTENCIA (CONSISTENCY)
-- Objetivo: Uniformidad contra catálogos nacionales (INEC 2024).
-- ------------------------------------------------------------------------------
-- [HALLAZGO CRÍTICO]: Provincias que no existen en el catálogo maestro
SELECT DISTINCT provincia 
FROM dw.dim_area 
WHERE sk_area > 0 
  AND provincia != 'N/A'
  AND provincia NOT IN (SELECT nombre_provincia FROM ref.inec_dpa_2024);

-- ------------------------------------------------------------------------------
-- 4. VALIDEZ (VALIDITY)
-- Objetivo: Datos dentro de rangos lógicos y formatos correctos.
-- ------------------------------------------------------------------------------
-- Verificación de porcentajes de intersección de riesgo ambiental
SELECT sk_proyecto, porcentaje_interseccion
FROM dw.bridge_interseccion_ambiental
WHERE porcentaje_interseccion < 0 OR porcentaje_interseccion > 100;

-- ------------------------------------------------------------------------------
-- 5. OPORTUNIDAD (TIMELINESS)
-- Objetivo: Datos disponibles en el tiempo esperado.
-- ------------------------------------------------------------------------------
SELECT 
    MAX(fecha_carga) as ultima_ingesta,
    now() as fecha_actual,
    now() - MAX(fecha_carga) as latencia_dato
FROM dw.dim_area;

-- ------------------------------------------------------------------------------
-- 6. AUDITORÍA AMBIENTAL Y TRAZABILIDAD (SENIOR UX)
-- ------------------------------------------------------------------------------
-- 6.1 Validación de Trazabilidad en Desechos (Códigos Proyecto y RGD)
-- El 100% de los registros de desechos deben tener un proyecto y generador asociado.
SELECT 
    f.waste_generation_key, 
    p.codigo_proyecto, 
    w.generator_name as rgd_fuente
FROM dw.fact_waste_generation f
LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_waste_generator w ON f.waste_generator_key = w.waste_generator_key
WHERE p.codigo_proyecto IS NULL OR w.generator_name IS NULL;

-- 6.2 Integridad de Jerarquía Ambiental (Bridge vs Fact)
-- Valida consistencia entre la bandera de SNAP en Fact y el detalle en la tabla puente.
SELECT p.codigo_proyecto, f.interseccion_snap
FROM dw.dim_proyecto p
JOIN dw.fact_regularizacion f ON p.sk_proyecto = f.sk_proyecto
LEFT JOIN dw.bridge_interseccion_ambiental b ON p.sk_proyecto = b.sk_proyecto
WHERE f.interseccion_snap = 'C' AND b.sk_proyecto IS NULL;
