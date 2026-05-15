-- ==============================================================================
-- etl_intersection_load.sql (v1.8.1)
-- ==============================================================================
-- Carga de certificados de intersección SNAP a la dimensión dw.dim_intersection.
-- Vincula la información de producción (179) con los proyectos locales (sk_proyecto).
-- ==============================================================================

-- 1. Marcar registros antiguos como is_current = FALSE (SCD Tipo 1 o 2 simplificado)
UPDATE dw.dim_intersection di
SET is_current = FALSE
FROM stg.stg_intersection stg
JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
WHERE di.sk_proyecto = dp.sk_proyecto
  AND di.certificate_code != stg.certificate_code;

-- 2. Insertar nuevos certificados o actualizar existentes
INSERT INTO dw.dim_intersection (
    sk_proyecto, certificate_code, certificate_date, 
    html_location, html_layers, dictamen_final, is_current
)
SELECT 
    dp.sk_proyecto,
    stg.certificate_code,
    stg.certificate_date,
    stg.html_location,
    stg.html_layers,
    stg.dictamen_final,
    TRUE
FROM stg.stg_intersection stg
JOIN dw.dim_proyecto dp ON stg.project_code = dp.codigo_proyecto
ON CONFLICT (sk_proyecto, certificate_code) DO UPDATE SET 
    certificate_date = EXCLUDED.certificate_date,
    html_location = EXCLUDED.html_location,
    html_layers = EXCLUDED.html_layers,
    dictamen_final = EXCLUDED.dictamen_final,
    is_current = TRUE;

-- 3. Análisis preventivo
ANALYZE dw.dim_intersection;
