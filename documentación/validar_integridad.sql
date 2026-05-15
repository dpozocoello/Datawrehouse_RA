-- ============================================================================
-- SCRIPT: Validar Integridad Estructural
-- Descripción: Verifica problemas comunes en diseño de BD
-- Autor: DBA PostgreSQL - MAATE
-- ============================================================================
--- '=========================================' --- 'VALIDACIÓN DE INTEGRIDAD ESTRUCTURAL' --- '=========================================' --- '' -- 1. TABLAS SIN PRIMARY KEY
--- '1. ⚠ TABLAS SIN CLAVE PRIMARIA' --- '------------------------------'
SELECT t.table_schema as esquema,
    t.table_name as tabla,
    '¡CRÍTICO! Agregar PK' as accion_requerida
FROM information_schema.tables t
    LEFT JOIN information_schema.table_constraints tc ON t.table_name = tc.table_name
    AND t.table_schema = tc.table_schema
    AND tc.constraint_type = 'PRIMARY KEY'
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
    AND t.table_type = 'BASE TABLE'
    AND tc.constraint_name IS NULL;
--- '' -- 2. FOREIGN KEYS SIN ÍNDICE
--- '2. ⚠ FOREIGN KEYS SIN ÍNDICE (Problema de rendimiento)' --- '-------------------------------------------------------'
SELECT DISTINCT tc.table_schema as esquema,
    tc.table_name as tabla,
    kcu.column_name as columna_fk,
    'Crear índice en esta columna' as recomendacion
FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    AND NOT EXISTS (
        SELECT 1
        FROM pg_indexes pi
        WHERE pi.schemaname = tc.table_schema
            AND pi.tablename = tc.table_name
            AND pi.indexdef LIKE '%' || kcu.column_name || '%'
    );
--- '' -- 3. COLUMNAS CON NOMBRES SOSPECHOSOS
--- '3. ℹ COLUMNAS CON NOMBRES POTENCIALMENTE PROBLEMÁTICOS' --- '------------------------------------------------------'
SELECT table_schema as esquema,
    table_name as tabla,
    column_name as columna,
    'Considerar renombrar' as sugerencia
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    AND (
        column_name LIKE '%date%'
        AND data_type NOT IN ('date', 'timestamp', 'timestamptz')
        OR column_name LIKE '%id%'
        AND data_type NOT IN ('integer', 'bigint', 'uuid')
        OR length(column_name) < 2
        OR column_name ~ '[A-Z]' -- CamelCase no recomendado en PG
    )
ORDER BY table_schema,
    table_name,
    column_name;
--- '' -- 4. TABLAS GRANDES SIN PARTICIONAMIENTO
--- '4. ℹ TABLAS GRANDES (Considerar particionamiento)' --- '-------------------------------------------------'
SELECT schemaname as esquema,
    tablename as tabla,
    pg_size_pretty(
        pg_total_relation_size(schemaname || '.' || tablename)
    ) as tamaño,
    'Evaluar particionamiento' as recomendacion
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    AND pg_total_relation_size(schemaname || '.' || tablename) > 10737418240 -- > 10GB
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;
--- '' -- 5. SECUENCIAS CERCA DEL LÍMITE
--- '5. ⚠ SEQUENCES CERCA DEL LÍMITE' --- '-------------------------------'
SELECT schemaname as esquema,
    sequencename as sequence,
    last_value,
    max_value,
    round(
        (last_value::numeric / max_value::numeric) * 100,
        2
    ) as porcentaje_usado,
    CASE
        WHEN (last_value::numeric / max_value::numeric) > 0.9 THEN '¡CRÍTICO!'
        WHEN (last_value::numeric / max_value::numeric) > 0.75 THEN 'Advertencia'
        ELSE 'OK'
    END as estado
FROM pg_sequences
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    AND (last_value::numeric / max_value::numeric) > 0.5 -- Más del 50% usado
ORDER BY porcentaje_usado DESC;
--- '' --- '=========================================' --- 'VALIDACIÓN COMPLETADA' --- 'Revise y corrija los problemas detectados' --- '========================================='