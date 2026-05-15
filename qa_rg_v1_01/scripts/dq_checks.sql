-- Data Quality Checks for Dashboard RG v1.01

-- 1. Completitud: Nulls en campos clave
-- FACT_REGULARIZACION
SELECT 'fact_regularizacion_nulls' as check_id, count(*) as fail_count
FROM dw.fact_regularizacion
WHERE sk_proyecto IS NULL OR sk_geografia IS NULL;

-- 2. Consistencia: Integridad Referencial (FKs sin correspondencia)
SELECT 'fk_orphans_geografia' as check_id, count(*) as fail_count
FROM dw.fact_regularizacion f
LEFT JOIN dw.dim_geografia d ON f.sk_geografia = d.sk_geografia
WHERE d.sk_geografia IS NULL;

-- 3. Duplicados: Registros repetidos por código de proyecto
SELECT 'duplicate_projects' as check_id, count(codigo_proyecto) - count(DISTINCT codigo_proyecto) as fail_count
FROM dw.fact_regularizacion;

-- 4. Validez: Dominios de estado
SELECT 'invalid_states' as check_id, count(*) as fail_count
FROM dw.fact_regularizacion
WHERE estado_consolidado NOT IN ('REGISTRADO', 'COMPLETADO', 'EN PROCESO', 'CANCELADO');

-- 5. Oportunidad: Datos sin actualizar > 48h
SELECT 'timeliness_lag' as check_id, count(*) as fail_count
FROM (SELECT max(fecha_carga) as last_load FROM dw.fact_regularizacion) t
WHERE last_load < now() - interval '48 hours';
